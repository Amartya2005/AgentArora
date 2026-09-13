/**
 * content.js
 * Member 1 — Browser Perception Layer (Day 1)
 * Orchestrates PageState capture and development-mode debug output.
 * No external network requests. No PII sanitization (that is Member 2's job).
 */

"use strict";

(function () {
  // Run after DOM is fully idle
  function run() {
    const pageState = window.__pageStateCapture();
    const errors = window.__pageStateValidate(pageState);

    // -----------------------------------------------------------------------
    // Debug output — development only
    // -----------------------------------------------------------------------
    console.group("=== PRIVACY-PRESERVING BROWSER AGENT ===");
    console.log("PAGE STATE");
    console.log(JSON.stringify(pageState, null, 2));
    console.groupEnd();

    if (errors.length === 0) {
      console.log("[PageState] ✅ Schema validation PASSED");
    } else {
      console.error("[PageState] ❌ Schema validation FAILED:");
      errors.forEach((e) => console.error("  •", e));
    }

    // -----------------------------------------------------------------------
    // Registry debug
    // -----------------------------------------------------------------------
    console.group("[PageState] Element Registry");
    window.__elementRegistry.forEach((el, id) => {
      const tag = el.tagName.toUpperCase();
      const label =
        el.getAttribute("aria-label") ||
        el.getAttribute("placeholder") ||
        el.textContent.trim().slice(0, 40) ||
        "(no label)";
      console.log(`${id} → ${tag} "${label}"`);
    });
    console.groupEnd();
  }

  if (document.readyState === "complete" || document.readyState === "interactive") {
    run();
  } else {
    document.addEventListener("DOMContentLoaded", run, { once: true });
  }
})();
