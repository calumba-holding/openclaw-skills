#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const operations = new Set(["env-check", "register", "detail", "disable"]);

function usage(exitCode = 0) {
  const message = `
Usage:
  build-service-request.mjs env-check [--operation register|detail|disable]
  build-service-request.mjs register --base-url URL --spec FILE [--api-key KEY] [--address ADDRESS]
  build-service-request.mjs detail --base-url URL --service-id SERVICE_ID [--api-key KEY]
  build-service-request.mjs disable --base-url URL --service-id SERVICE_ID [--api-key KEY]

Defaults:
  --api-key reads from AICADE_API_KEY when omitted.
  --address reads from AICADE_WALLET_ADDRESS when omitted.

This script prints a curl command only. It does not call the API.
`;
  console.log(message.trim());
  process.exit(exitCode);
}

function parseArgs(argv) {
  const [operation, ...rest] = argv;
  if (!operations.has(operation)) usage(1);

  const args = { command: operation };
  for (let index = 0; index < rest.length; index += 1) {
    const token = rest[index];
    if (token === "--help" || token === "-h") usage(0);
    if (!token.startsWith("--")) {
      throw new Error(`Unexpected positional argument: ${token}`);
    }

    const key = token.slice(2);
    const value = rest[index + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`Missing value for --${key}`);
    }
    args[key] = value;
    index += 1;
  }

  return args;
}

function buildEnvCheck(args) {
  const operation = args.operation || "detail";
  const needsWallet = operation === "register";
  const result = {
    operation,
    AICADE_API_KEY: Boolean(process.env.AICADE_API_KEY),
    AICADE_WALLET_ADDRESS: Boolean(process.env.AICADE_WALLET_ADDRESS),
    ready: Boolean(process.env.AICADE_API_KEY) && (!needsWallet || Boolean(process.env.AICADE_WALLET_ADDRESS)),
  };

  return JSON.stringify(result, null, 2);
}

function requireArg(args, key) {
  if (!args[key]) throw new Error(`Missing required --${key}`);
  return args[key];
}

function getApiKey(args) {
  const apiKey = args["api-key"] || process.env.AICADE_API_KEY;
  if (!apiKey) {
    throw new Error("Missing AICADE_API_KEY environment variable or --api-key");
  }
  return apiKey;
}

function getAddress(args) {
  const address = args.address || process.env.AICADE_WALLET_ADDRESS;
  if (!address) {
    throw new Error("Missing AICADE_WALLET_ADDRESS environment variable or --address");
  }
  return address;
}

function shellQuote(value) {
  return `'${String(value).replaceAll("'", "'\\''")}'`;
}

function joinUrl(baseUrl, apiPath) {
  return `${baseUrl.replace(/\/+$/, "")}${apiPath}`;
}

function validateRegisterSpec(spec) {
  const required = [
    "service_id",
    "service_name",
    "endpoint_url",
    "auth_type",
    "route_path",
    "input_schema",
    "output_schema",
    "billing",
  ];

  const missing = required.filter((key) => spec[key] === undefined || spec[key] === null);
  if (missing.length) {
    throw new Error(`Register spec missing required field(s): ${missing.join(", ")}`);
  }

  if (!/^[a-z0-9-]{3,64}$/.test(spec.service_id)) {
    throw new Error("service_id must use lowercase letters, digits, hyphens, length 3-64");
  }

  if (!String(spec.route_path).startsWith("/")) {
    throw new Error("route_path must start with /");
  }

  if (spec.timeout_ms !== undefined && (spec.timeout_ms < 1000 || spec.timeout_ms > 300000)) {
    throw new Error("timeout_ms must be between 1000 and 300000");
  }

  if (spec.strip_prefix !== undefined && (spec.strip_prefix < 0 || spec.strip_prefix > 10)) {
    throw new Error("strip_prefix must be between 0 and 10");
  }

  const billing = spec.billing || {};
  for (const key of ["billing_type", "currency", "fallback_strategy"]) {
    if (billing[key] === undefined || billing[key] === null) {
      throw new Error(`billing.${key} is required`);
    }
  }

  if (spec.auth_type !== "NONE" && spec.outbound_auth?.type && spec.outbound_auth.type !== spec.auth_type) {
    throw new Error("outbound_auth.type should match auth_type");
  }
}

function buildRegister(args) {
  const baseUrl = requireArg(args, "base-url");
  const apiKey = getApiKey(args);
  const address = getAddress(args);
  const specPath = path.resolve(requireArg(args, "spec"));
  const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
  validateRegisterSpec(spec);

  return [
    "curl",
    "-X",
    "POST",
    shellQuote(joinUrl(baseUrl, "/services")),
    "-H",
    shellQuote("Content-Type: application/json"),
    "-H",
    shellQuote(`X-API-Key: ${apiKey}`),
    "-H",
    shellQuote(`X-Address: ${address}`),
    "--data",
    shellQuote(JSON.stringify(spec, null, 2)),
  ].join(" ");
}

function buildDetail(args) {
  const baseUrl = requireArg(args, "base-url");
  const apiKey = getApiKey(args);
  const serviceId = encodeURIComponent(requireArg(args, "service-id"));

  return [
    "curl",
    "-X",
    "GET",
    shellQuote(joinUrl(baseUrl, `/services/${serviceId}`)),
    "-H",
    shellQuote(`X-API-Key: ${apiKey}`),
  ].join(" ");
}

function buildDisable(args) {
  const baseUrl = requireArg(args, "base-url");
  const apiKey = getApiKey(args);
  const serviceId = encodeURIComponent(requireArg(args, "service-id"));

  return [
    "curl",
    "-X",
    "POST",
    shellQuote(joinUrl(baseUrl, `/services/disable?serviceId=${serviceId}`)),
    "-H",
    shellQuote(`X-API-Key: ${apiKey}`),
  ].join(" ");
}

try {
  const args = parseArgs(process.argv.slice(2));
  const builders = {
    "env-check": buildEnvCheck,
    register: buildRegister,
    detail: buildDetail,
    disable: buildDisable,
  };

  console.log(builders[args.command](args));
} catch (error) {
  console.error(`Error: ${error.message}`);
  console.error("Run with --help for usage.");
  process.exit(1);
}
