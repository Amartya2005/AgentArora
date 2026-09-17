"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

function element(tagName, props = {}) {
  const attributes = new Map(Object.entries(props.attributes || {}));
  return {
    tagName,
    isConnected: true,
    disabled: Boolean(props.disabled),
    readOnly: Boolean(props.readOnly),
    value: props.value || "",
    options: props.options || [],
    parentElement: null,
    style: props.style || {},
    events: [],
    getAttribute(name) { return attributes.get(name) ?? null; },
    setAttribute(name, value) { attributes.set(name, String(value)); },
    hasAttribute(name) { return attributes.has(name); },
    getBoundingClientRect() { return { width: 100, height: 30 }; },
    focus() { this.focused = true; },
    dispatchEvent(event) { this.events.push(event.type); return true; },
    click() { this.clicked = true; this.clicks = (this.clicks || 0) + 1; },
  };
}

function plan(action) {
  return {
    schema_version: "1.0",
    action_plan_id: "AP_test_001",
    source_sanitized_state_id: "SPS_test_001",
    created_at: "2026-09-15T00:00:00Z",
    intent: "Test action",
    actions: [action],
  };
}

function load() {
  const context = {
    console,
    Date,
    Map,
    Set,
    Array,
    Number,
    Object,
    Promise,
    isNaN,
    Event: class Event { constructor(type) { this.type = type; } },
    KeyboardEvent: class KeyboardEvent { constructor(type, init) { this.type = type; Object.assign(this, init); } },
    setTimeout,
    window: {
      getComputedStyle: (el) => el.style || {},
      scrollBy: (...args) => { context.window.scrolled = args; },
      __elementRegistry: new Map(),
      __elementIdentities: new Map(),
      __captureFreshPageState: () => { context.window.freshCaptures = (context.window.freshCaptures || 0) + 1; },
      chrome: { runtime: { onMessage: { addListener() {} } } },
    },
    document: { activeElement: null, dispatchEvent() {} },
  };
  context.window.__targetIdentityForElement = (el) => ({
    tag: el.tagName.toLowerCase(),
    role: (el.getAttribute("role") || el.tagName.toLowerCase()),
    label: el.getAttribute("aria-label") || "",
    type: (el.getAttribute("type") || (el.tagName === "INPUT" ? "text" : el.tagName.toLowerCase())).toLowerCase(),
  });
  context.window.__resolveTargetIdentity = (id) => context.window.__elementIdentities.get(id) || null;
  context.globalThis = context;
  vm.runInNewContext(fs.readFileSync(require.resolve("../extension/action-handler.js"), "utf8"), context);
  return context;
}

function register(context, id, el) {
  context.window.__elementRegistry.set(id, { deref: () => el });
  context.window.__elementIdentities.set(id, context.window.__targetIdentityForElement(el));
}

function assertActionResult(result) {
  assert.deepEqual(
    Object.keys(result).sort(),
    ["action_id", "action_plan_id", "completed_at", "error", "needs_fresh_page_state", "observed_change", "schema_version", "status"].sort().filter((key) => key !== "error" || result.error !== undefined)
  );
  assert.equal(result.schema_version, "1.0");
  assert.match(result.action_plan_id, /^AP_[A-Za-z0-9_-]{6,64}$/);
  assert.match(result.action_id, /^ACT_[A-Za-z0-9_-]{6,64}$/);
  assert.equal(typeof result.needs_fresh_page_state, "boolean");
  assert.equal(typeof result.observed_change, "string");
  if (result.status !== "SUCCESS") assert.ok(result.error && result.error.code && typeof result.error.message === "string");
}

async function run() {
  const context = load();
  const button = element("BUTTON");
  const input = element("INPUT", { attributes: { type: "text" } });
  const stale = element("BUTTON");
  stale.isConnected = false;
  register(context, "EL_001", button);
  register(context, "EL_002", input);
  register(context, "EL_003", stale);

  let results = await context.window.__executeActionPlan(plan({ action_id: "ACT_click01", action_type: "CLICK", target_element_id: "EL_001", reason: "Click", risk_level: "LOW" }));
  assertActionResult(results[0]);
  assert.equal(results[0].status, "SUCCESS");
  assert.equal(button.clicked, true);
  assert.equal(button.clicks, 1);

  results = await context.window.__executeActionPlan(plan({ action_id: "ACT_type01", action_type: "TYPE", target_element_id: "EL_002", input: { source: "SAFE_LITERAL", value: "demo" }, reason: "Type", risk_level: "LOW" }));
  assertActionResult(results[0]);
  assert.equal(results[0].status, "SUCCESS");
  assert.equal(input.value, "demo");
  assert.deepEqual(input.events, ["input", "change"]);

  results = await context.window.__executeActionPlan(plan({ action_id: "ACT_scroll01", action_type: "SCROLL", scroll: { direction: "DOWN", amount: "MEDIUM" }, reason: "Scroll", risk_level: "LOW" }));
  assertActionResult(results[0]);
  assert.equal(results[0].status, "SUCCESS");
  assert.deepEqual(context.window.scrolled, [0, 600]);

  const select = element("SELECT", { options: [{ value: "all", textContent: "All" }, { value: "food", textContent: "Food" }] });
  register(context, "EL_005", select);
  results = await context.window.__executeActionPlan(plan({ action_id: "ACT_select01", action_type: "SELECT", target_element_id: "EL_005", select: { option: "Food" }, reason: "Select", risk_level: "LOW" }));
  assertActionResult(results[0]);
  assert.equal(results[0].status, "SUCCESS");
  assert.equal(select.value, "food");

  context.document.activeElement = button;
  results = await context.window.__executeActionPlan(plan({ action_id: "ACT_key001", action_type: "PRESS_KEY", key: "ENTER", reason: "Press", risk_level: "LOW" }));
  assertActionResult(results[0]);
  assert.equal(results[0].status, "SUCCESS");
  assert.deepEqual(button.events.slice(-2), ["keydown", "keyup"]);

  results = await context.window.__executeActionPlan(plan({ action_id: "ACT_wait01", action_type: "WAIT", wait_ms: 100, reason: "Wait", risk_level: "LOW" }));
  assertActionResult(results[0]);
  assert.equal(results[0].status, "SUCCESS");

  const clicksBeforeUnknown = button.clicks;
  results = await context.window.__executeActionPlan(plan({ action_id: "ACT_unknown", action_type: "CLICK", target_element_id: "EL_999", reason: "Unknown", risk_level: "LOW" }));
  assertActionResult(results[0]);
  assert.equal(results[0].status, "INVALID_ACTION");
  assert.equal(results[0].error.code, "INVALID_ACTION");
  assert.equal(button.clicks, clicksBeforeUnknown);

  const capturesBeforeStale = context.window.freshCaptures || 0;
  results = await context.window.__executeActionPlan(plan({ action_id: "ACT_stale01", action_type: "CLICK", target_element_id: "EL_003", reason: "Stale", risk_level: "LOW" }));
  assertActionResult(results[0]);
  assert.equal(results[0].status, "STALE_ELEMENT");
  assert.equal(results[0].needs_fresh_page_state, true);
  assert.equal(context.window.freshCaptures, capturesBeforeStale + 1);

  const disabled = element("BUTTON", { disabled: true });
  register(context, "EL_004", disabled);
  results = await context.window.__executeActionPlan(plan({ action_id: "ACT_disable", action_type: "CLICK", target_element_id: "EL_004", reason: "Disabled", risk_level: "LOW" }));
  assertActionResult(results[0]);
  assert.equal(results[0].status, "BLOCKED_BY_POLICY");
  assert.equal(results[0].error.code, "POLICY_BLOCKED");
  assert.equal(disabled.clicked, undefined);
  assert.equal(results[0].needs_fresh_page_state, true);

  const hidden = element("BUTTON", { style: { display: "none" } });
  register(context, "EL_006", hidden);
  results = await context.window.__executeActionPlan(plan({ action_id: "ACT_hidden1", action_type: "CLICK", target_element_id: "EL_006", reason: "Hidden", risk_level: "LOW" }));
  assert.equal(results[0].status, "STALE_ELEMENT");
  assert.equal(results[0].error.code, "STALE_ELEMENT");
  assert.equal(results[0].needs_fresh_page_state, true);
  assert.equal(hidden.clicked, undefined);

  const relabeled = element("BUTTON", { attributes: { "aria-label": "Continue" } });
  register(context, "EL_007", relabeled);
  relabeled.setAttribute("aria-label", "Delete");
  results = await context.window.__executeActionPlan(plan({ action_id: "ACT_label01", action_type: "CLICK", target_element_id: "EL_007", reason: "Changed label", risk_level: "LOW" }));
  assert.equal(results[0].status, "STALE_ELEMENT");
  assert.equal(results[0].error.code, "STALE_ELEMENT");
  assert.equal(results[0].needs_fresh_page_state, true);
  assert.equal(relabeled.clicked, undefined);

  const rerendered = element("BUTTON", { attributes: { "aria-label": "Continue" } });
  register(context, "EL_008", rerendered);
  rerendered.setAttribute("role", "link");
  results = await context.window.__executeActionPlan(plan({ action_id: "ACT_role001", action_type: "CLICK", target_element_id: "EL_008", reason: "Changed role", risk_level: "LOW" }));
  assert.equal(results[0].status, "STALE_ELEMENT");
  assert.equal(results[0].error.code, "STALE_ELEMENT");
  assert.equal(rerendered.clicked, undefined);

  const ariaDisabled = element("BUTTON");
  register(context, "EL_009", ariaDisabled);
  ariaDisabled.setAttribute("aria-disabled", "true");
  results = await context.window.__executeActionPlan(plan({ action_id: "ACT_aria001", action_type: "CLICK", target_element_id: "EL_009", reason: "ARIA disabled", risk_level: "LOW" }));
  assert.equal(results[0].status, "BLOCKED_BY_POLICY");
  assert.equal(results[0].error.code, "POLICY_BLOCKED");
  assert.equal(ariaDisabled.clicked, undefined);

  const missingTarget = { action_id: "ACT_missing1", action_type: "CLICK", reason: "Missing target", risk_level: "LOW" };
  results = await context.window.__executeActionPlan(plan(missingTarget));
  assert.equal(results[0].status, "INVALID_ACTION");
  assert.equal(results[0].error.code, "SCHEMA_VALIDATION_FAILED");

  const jsTarget = element("BUTTON");
  register(context, "EL_010", jsTarget);
  context.window.jsExecuted = false;
  results = await context.window.__executeActionPlan(plan({ action_id: "ACT_jsblock", action_type: "CLICK", target_element_id: "EL_010", reason: "javascript:window.jsExecuted = true", risk_level: "LOW" }));
  assert.equal(results[0].status, "INVALID_ACTION");
  assert.equal(results[0].error.code, "SCHEMA_VALIDATION_FAILED");
  assert.equal(context.window.jsExecuted, false);
  assert.equal(jsTarget.clicked, undefined);

  assert.ok(context.window.freshCaptures >= 3);

  results = await context.window.__executeActionPlan(plan({ action_id: "ACT_badact", action_type: "DELETE_DATABASE", reason: "Invalid", risk_level: "HIGH" }));
  assertActionResult(results[0]);
  assert.equal(results[0].status, "INVALID_ACTION");
  assert.equal(results[0].error.code, "SCHEMA_VALIDATION_FAILED");

  console.log("action-handler tests: PASS");
}

run().catch((error) => { console.error(error); process.exitCode = 1; });
