#!/usr/bin/env node
import { constants } from "node:fs";
import { access } from "node:fs/promises";
import { homedir } from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

function parseArgs(argv) {
  const args = {
    local: false,
    cloud: false,
    apiKey: "",
    memoryDir: "",
  };

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--local") {
      args.local = true;
      continue;
    }
    if (value === "--cloud") {
      args.cloud = true;
      continue;
    }
    if (value === "--api-key") {
      args.apiKey = argv[index + 1] || "";
      index += 1;
      continue;
    }
    if (value === "--memory-dir") {
      args.memoryDir = argv[index + 1] || "";
      index += 1;
    }
  }

  return args;
}

async function ensureReadable(filePath) {
  await access(filePath, constants.R_OK);
}

async function importFromPlugin(pluginRoot, relativePath) {
  const absolutePath = path.join(pluginRoot, relativePath);
  await ensureReadable(absolutePath);
  return import(pathToFileURL(absolutePath).href);
}

const args = parseArgs(process.argv.slice(2));
const openclawHome = path.join(homedir(), ".openclaw");
const pluginRoot = path.join(openclawHome, "node_modules", "@echomem", "echo-memory-cloud-openclaw-plugin");
const workspaceDir = path.join(openclawHome, "workspace");

try {
  await ensureReadable(path.join(pluginRoot, "package.json"));
} catch {
  console.error("EchoMemory plugin was not found under ~/.openclaw/node_modules.");
  console.error("Install the plugin first, then restart the gateway or rerun this script.");
  process.exit(1);
}

const [{ buildConfig }, { createApiClient }, { startLocalServer }] = await Promise.all([
  importFromPlugin(pluginRoot, "lib/config.js"),
  importFromPlugin(pluginRoot, "lib/api-client.js"),
  importFromPlugin(pluginRoot, "lib/local-server.js"),
]);

const overrideConfig = {};
if (args.local) {
  overrideConfig.localOnlyMode = true;
}
if (args.cloud) {
  overrideConfig.localOnlyMode = false;
}
if (args.apiKey) {
  overrideConfig.apiKey = args.apiKey;
}
if (args.memoryDir) {
  overrideConfig.memoryDir = args.memoryDir;
}

const cfg = buildConfig(overrideConfig);
const client = !cfg.localOnlyMode && cfg.apiKey ? createApiClient(cfg) : null;

console.log("EchoMemory manual local UI startup");
console.log(`Mode: ${cfg.localOnlyMode ? "local" : "cloud"}`);
console.log(`Memory dir: ${cfg.memoryDir}`);
console.log(`API key: ${cfg.apiKey ? `${cfg.apiKey.slice(0, 3)}...${cfg.apiKey.slice(-3)}` : "not set"}`);

const url = await startLocalServer(workspaceDir, {
  apiClient: client,
  cfg,
  syncRunner: null,
});

console.log(`Local workspace viewer: ${url}`);
