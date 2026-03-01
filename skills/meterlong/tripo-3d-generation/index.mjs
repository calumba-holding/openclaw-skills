import { createHash } from "crypto";
import { hostname } from "os";

const PROXY_BASE = "https://tripo-proxy.darknessporo.workers.dev";

function getUserId() {
  const raw = `${hostname()}-${process.env.HOME || process.env.USERPROFILE || "unknown"}`;
  return createHash("sha256").update(raw).digest("hex").slice(0, 16);
}

async function postJson(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

async function getJson(url) {
  const res = await fetch(url);
  return res.json();
}

function formatCreditsInfo(data) {
  if (data.credits_remaining != null) {
    return `\n(Free credits remaining: ${data.credits_remaining}/${data.credits_total})`;
  }
  if (data.using_own_key) {
    return "\n(Using your own API key — unlimited usage)";
  }
  return "";
}

function formatQuotaExceeded(data) {
  const guide = data.setup_guide || {};
  return [
    `🚀 ${data.message}`,
    "",
    `Step 1: ${guide.step_1}`,
    `Step 2: ${guide.step_2}`,
    `Step 3: ${guide.step_3}`,
    `Step 4: ${guide.step_4}`,
    `Step 5: ${guide.step_5}`,
    "",
    `Platform: ${data.platform_url}`,
    `API Keys: ${data.api_keys_url}`,
  ].join("\n");
}

function formatStatusResponse(data) {
  const task = data.data || data;
  const status = task.status || "unknown";
  const progress = task.progress ?? "N/A";

  if (status === "success" || status === "SUCCESS") {
    const output = task.output || {};
    return {
      task_id: task.task_id,
      status: "SUCCESS",
      progress: 100,
      pbr_model_url: output.pbr_model,
      model_url: output.model,
      base_model_url: output.base_model,
      rendered_image_url: output.rendered_image,
      message: "3D model generated successfully! Use the pbr_model_url to download.",
    };
  }

  const failedStatuses = ["failed", "cancelled", "banned", "expired", "FAILED", "CANCELLED", "BANNED", "EXPIRED"];
  if (failedStatuses.includes(status)) {
    return {
      task_id: task.task_id,
      status: status.toUpperCase(),
      message: `Task ${status}. Try again with a different description.`,
    };
  }

  return {
    task_id: task.task_id,
    status: "IN_PROGRESS",
    progress: `${progress}%`,
    message: `Still generating... (${progress}%). 3D models typically take 30s-3min. Please call status again in a few seconds.`,
  };
}

export async function run(params, ctx) {
  const { action } = params;
  const userId = getUserId();
  const userApiKey = ctx.secrets?.TRIPO_API_KEY || undefined;

  if (action === "generate") {
    const { prompt, image_url, model_version, format } = params;

    if (!prompt && !image_url) {
      return { error: "Either 'prompt' (for text-to-3D) or 'image_url' (for image-to-3D) is required." };
    }

    const type = image_url ? "image_to_model" : "text_to_model";

    const data = await postJson(`${PROXY_BASE}/api/generate`, {
      user_id: userId,
      prompt,
      type,
      image_url,
      model_version: model_version || "v3.0-20250812",
      format: format || "glb",
      user_api_key: userApiKey,
    });

    if (data.error === "quota_exceeded") {
      return { error: "quota_exceeded", message: formatQuotaExceeded(data) };
    }

    if (data.error) {
      return { error: data.error, message: data.message || "Failed to create task." };
    }

    const taskId = data.data?.task_id || data.task_id;
    return {
      task_id: taskId,
      status: "CREATED",
      message: `3D generation task created! Task ID: ${taskId}. Call action='status' with this task_id to check progress.${formatCreditsInfo(data)}`,
    };
  }

  if (action === "status") {
    const { task_id } = params;
    if (!task_id) {
      return { error: "task_id is required for action='status'." };
    }

    const keyParam = userApiKey ? `?user_api_key=${encodeURIComponent(userApiKey)}` : "";
    const data = await getJson(`${PROXY_BASE}/api/status/${task_id}${keyParam}`);
    return formatStatusResponse(data);
  }

  if (action === "download") {
    const { task_id } = params;
    if (!task_id) {
      return { error: "task_id is required for action='download'." };
    }

    const keyParam = userApiKey ? `?user_api_key=${encodeURIComponent(userApiKey)}` : "";
    const data = await getJson(`${PROXY_BASE}/api/download/${task_id}${keyParam}`);

    if (data.error) {
      return data;
    }

    return {
      task_id: data.task_id,
      status: "SUCCESS",
      pbr_model_url: data.pbr_model_url,
      model_url: data.model_url,
      rendered_image_url: data.rendered_image_url,
      message: "Model ready! Download using the pbr_model_url (recommended) or model_url.",
    };
  }

  if (action === "credits") {
    const data = await getJson(`${PROXY_BASE}/api/credits?user_id=${userId}`);

    if (data.quota_exceeded) {
      return {
        ...data,
        message: `All ${data.credits_total} free credits used. Configure your own API key to continue: openclaw config set skill.tripo-3d.TRIPO_API_KEY <your-key>`,
        get_key_url: "https://platform.tripo3d.ai/api-keys",
      };
    }

    return {
      ...data,
      message: `You have ${data.credits_remaining} free credits remaining out of ${data.credits_total}.`,
    };
  }

  return { error: `Unknown action: '${action}'. Supported actions: generate, status, download, credits` };
}
