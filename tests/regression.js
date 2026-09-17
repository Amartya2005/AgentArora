"use strict";

(async function () {
  function entryFor(state, element) {
    for (const [id, ref] of window.__elementRegistry) {
      const node = ref.deref ? ref.deref() : ref;
      if (node === element) {
        return state.elements.find((entry) => entry.element_id === id);
      }
    }
    return undefined;
  }

  function assert(condition, message, failures) {
    if (!condition) failures.push(message);
  }

  function clickPlan(id, actionId) {
    return {
      schema_version: "1.0",
      action_plan_id: "AP_regression_001",
      source_sanitized_state_id: "SPS_regression_001",
      created_at: new Date().toISOString(),
      intent: "Exercise dynamic target safety.",
      actions: [{
        action_id: actionId,
        action_type: "CLICK",
        target_element_id: id,
        reason: "Regression safety check.",
        risk_level: "LOW",
      }],
    };
  }

  function typePlan(id, actionId) {
    const plan = clickPlan(id, actionId);
    plan.actions[0].action_type = "TYPE";
    plan.actions[0].input = { source: "SAFE_LITERAL", value: "demo" };
    return plan;
  }

  async function execute(plan) {
    return (await window.__executeActionPlan(plan))[0];
  }

  const failures = [];
  const fixture = document.createElement("div");
  fixture.id = "member1-regression-fixture";
  fixture.innerHTML = [
    '<button id="reg-native-disabled" disabled>Disabled</button>',
    '<button id="reg-native-aria-disabled" aria-disabled="true">ARIA disabled</button>',
    '<div id="reg-div-aria-disabled" role="button" aria-disabled="true">ARIA div</div>',
    '<button id="reg-enabled">Enabled</button>',
    '<div id="reg-opacity-parent" style="opacity: 0">',
    '  <button id="reg-opacity-child">Transparent child</button>',
    '</div>',
  ].join("");
  document.body.appendChild(fixture);

  const state = window.__pageStateCapture();
  const nativeDisabled = entryFor(state, document.getElementById("reg-native-disabled"));
  const nativeAriaDisabled = entryFor(state, document.getElementById("reg-native-aria-disabled"));
  const divAriaDisabled = entryFor(state, document.getElementById("reg-div-aria-disabled"));
  const enabled = entryFor(state, document.getElementById("reg-enabled"));
  const opacityChild = entryFor(state, document.getElementById("reg-opacity-child"));

  const oldId = nativeDisabled && nativeDisabled.element_id;
  const oldElement = document.getElementById("reg-native-disabled");
  const secondState = window.__pageStateCapture();
  const secondNativeDisabled = entryFor(secondState, oldElement);
  const currentId = secondNativeDisabled && secondNativeDisabled.element_id;

  assert(nativeDisabled && nativeDisabled.enabled === false, "native disabled control must be disabled", failures);
  assert(nativeAriaDisabled && nativeAriaDisabled.enabled === false, "native aria-disabled control must be disabled", failures);
  assert(divAriaDisabled && divAriaDisabled.enabled === false, "ARIA-disabled role control must be disabled", failures);
  assert(enabled && enabled.enabled === true, "normal native control must remain enabled", failures);
  assert(opacityChild && opacityChild.visible === false, "opacity-hidden descendant must be invisible", failures);
  assert(oldId && currentId && oldId !== currentId, "recapture must not reuse an old element ID", failures);
  assert(window.__resolveRegistryEntry(oldId) === null, "old capture element ID must be stale", failures);
  assert(currentId && window.__resolveRegistryEntry(currentId) === oldElement, "current capture element ID must resolve", failures);
  const thirdState = window.__pageStateCapture();
  assert(window.__resolveRegistryEntry(currentId) === null, "previous capture ID must be stale after another recapture", failures);
  assert(thirdState.elements.every((entry) => /^EL_[0-9]{3,6}$/.test(entry.element_id)), "repeated capture IDs must remain valid", failures);
  assert(window.__pageStateValidate(state).length === 0, "generated PageState must pass validation", failures);
  assert(!JSON.stringify(state).includes("SuperSecret123!"), "password value must not appear in PageState", failures);

  const normal = document.createElement("button");
  normal.textContent = "Normal click";
  fixture.appendChild(normal);
  let dynamicState = window.__pageStateCapture();
  const normalId = entryFor(dynamicState, normal).element_id;
  let normalClicks = 0;
  normal.addEventListener("click", () => { normalClicks += 1; });
  let actionResult = await execute(clickPlan(normalId, "ACT_normal_001"));
  assert(actionResult.status === "SUCCESS" && normalClicks === 1, "captured button must execute a normal click once", failures);

  const removed = document.createElement("button");
  removed.textContent = "Remove me";
  fixture.appendChild(removed);
  dynamicState = window.__pageStateCapture();
  const removedId = entryFor(dynamicState, removed).element_id;
  let clicks = 0;
  removed.addEventListener("click", () => { clicks += 1; });
  removed.remove();
  actionResult = await execute(clickPlan(removedId, "ACT_remove_001"));
  assert(actionResult.status === "STALE_ELEMENT" && actionResult.error.code === "STALE_ELEMENT", "removed target must return STALE_ELEMENT", failures);
  assert(actionResult.needs_fresh_page_state === true && clicks === 0, "removed target must not click and must request fresh state", failures);

  const replacementHost = document.createElement("div");
  replacementHost.innerHTML = '<button aria-label="Original">Original</button>';
  fixture.appendChild(replacementHost);
  const original = replacementHost.firstElementChild;
  dynamicState = window.__pageStateCapture();
  const originalId = entryFor(dynamicState, original).element_id;
  let replacementClicks = 0;
  replacementHost.innerHTML = '<button aria-label="Replacement">Replacement</button>';
  const replacement = replacementHost.firstElementChild;
  replacement.addEventListener("click", () => { replacementClicks += 1; });
  actionResult = await execute(clickPlan(originalId, "ACT_replace_001"));
  assert(actionResult.status === "STALE_ELEMENT" && actionResult.error.code === "STALE_ELEMENT" && replacementClicks === 0, "replaced target must not select the replacement node", failures);
  const replacementState = window.__pageStateCapture();
  const replacementEntry = entryFor(replacementState, replacement);
  assert(replacementEntry && replacementEntry.element_id !== originalId && replacementEntry.label === "Replacement", "fresh PageState must describe the replacement with a new ID", failures);
  assert(window.__resolveRegistryEntry(originalId) === null, "old replacement ID must remain stale after fresh capture", failures);

  const rerenderHost = document.createElement("div");
  rerenderHost.innerHTML = '<button aria-label="Rerender">Rerender</button>';
  fixture.appendChild(rerenderHost);
  const rerenderedOld = rerenderHost.firstElementChild;
  dynamicState = window.__pageStateCapture();
  const rerenderedId = entryFor(dynamicState, rerenderedOld).element_id;
  rerenderHost.innerHTML = '<button aria-label="Rerender">Rerender</button>';
  const rerenderedNew = rerenderHost.firstElementChild;
  let rerenderClicks = 0;
  rerenderedNew.addEventListener("click", () => { rerenderClicks += 1; });
  actionResult = await execute(clickPlan(rerenderedId, "ACT_rerender01"));
  assert(actionResult.status === "STALE_ELEMENT" && actionResult.error.code === "STALE_ELEMENT" && rerenderClicks === 0, "rerendered target must reject its old node ID", failures);

  const hidden = document.createElement("button");
  hidden.textContent = "Hide me";
  fixture.appendChild(hidden);
  dynamicState = window.__pageStateCapture();
  const hiddenId = entryFor(dynamicState, hidden).element_id;
  let hiddenClicks = 0;
  hidden.addEventListener("click", () => { hiddenClicks += 1; });
  hidden.style.display = "none";
  actionResult = await execute(clickPlan(hiddenId, "ACT_hidden_001"));
  assert(actionResult.status === "STALE_ELEMENT" && actionResult.error.code === "STALE_ELEMENT" && actionResult.needs_fresh_page_state === true && hiddenClicks === 0, "hidden target must be stale without a click", failures);

  const disabled = document.createElement("button");
  disabled.textContent = "Disable me";
  fixture.appendChild(disabled);
  dynamicState = window.__pageStateCapture();
  const disabledId = entryFor(dynamicState, disabled).element_id;
  let disabledClicks = 0;
  disabled.addEventListener("click", () => { disabledClicks += 1; });
  disabled.disabled = true;
  actionResult = await execute(clickPlan(disabledId, "ACT_disable_001"));
  assert(actionResult.status === "BLOCKED_BY_POLICY" && actionResult.error.code === "POLICY_BLOCKED" && actionResult.needs_fresh_page_state === true && disabledClicks === 0, "disabled target must be blocked without a click", failures);

  const ariaDisabled = document.createElement("button");
  ariaDisabled.textContent = "ARIA disable me";
  fixture.appendChild(ariaDisabled);
  dynamicState = window.__pageStateCapture();
  const ariaDisabledId = entryFor(dynamicState, ariaDisabled).element_id;
  let ariaDisabledClicks = 0;
  ariaDisabled.addEventListener("click", () => { ariaDisabledClicks += 1; });
  ariaDisabled.setAttribute("aria-disabled", "true");
  actionResult = await execute(clickPlan(ariaDisabledId, "ACT_ariaoff_001"));
  assert(actionResult.status === "BLOCKED_BY_POLICY" && actionResult.error.code === "POLICY_BLOCKED" && ariaDisabledClicks === 0, "ARIA-disabled target must be blocked without a click", failures);

  const relabeled = document.createElement("button");
  relabeled.setAttribute("aria-label", "Continue");
  relabeled.textContent = "Continue";
  fixture.appendChild(relabeled);
  dynamicState = window.__pageStateCapture();
  const relabeledId = entryFor(dynamicState, relabeled).element_id;
  let relabeledClicks = 0;
  relabeled.addEventListener("click", () => { relabeledClicks += 1; });
  relabeled.setAttribute("aria-label", "Delete");
  actionResult = await execute(clickPlan(relabeledId, "ACT_relabel_001"));
  assert(actionResult.status === "STALE_ELEMENT" && actionResult.error.code === "STALE_ELEMENT" && relabeledClicks === 0, "label change must reject the target", failures);

  const roleChanged = document.createElement("div");
  roleChanged.setAttribute("role", "button");
  roleChanged.setAttribute("aria-label", "Continue");
  roleChanged.textContent = "Continue";
  fixture.appendChild(roleChanged);
  dynamicState = window.__pageStateCapture();
  const roleChangedId = entryFor(dynamicState, roleChanged).element_id;
  let roleChangedClicks = 0;
  roleChanged.addEventListener("click", () => { roleChangedClicks += 1; });
  roleChanged.setAttribute("role", "link");
  actionResult = await execute(clickPlan(roleChangedId, "ACT_rolechg_001"));
  assert(actionResult.status === "STALE_ELEMENT" && actionResult.error.code === "STALE_ELEMENT" && roleChangedClicks === 0, "role change must reject the target", failures);

  const typeChanged = document.createElement("input");
  typeChanged.type = "text";
  typeChanged.setAttribute("aria-label", "Search");
  fixture.appendChild(typeChanged);
  dynamicState = window.__pageStateCapture();
  const typeChangedId = entryFor(dynamicState, typeChanged).element_id;
  typeChanged.type = "email";
  actionResult = await execute(typePlan(typeChangedId, "ACT_typechg_001"));
  assert(actionResult.status === "STALE_ELEMENT" && actionResult.error.code === "STALE_ELEMENT" && typeChanged.value === "", "type change must reject text entry", failures);

  fixture.remove();
  const result = { passed: failures.length === 0, failures };
  window.__member1RegressionResults = result;
  console.log(`[Member1 regression] ${result.passed ? "PASS" : "FAIL"}`, result);
})().catch((error) => {
  window.__member1RegressionResults = { passed: false, failures: ["Regression execution failed."] };
  console.error("[Member1 regression] FAIL", error);
});
