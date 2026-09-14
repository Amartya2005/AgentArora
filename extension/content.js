/**
 * content.js
 * Member 1 — Browser Perception Layer (Day 1)
 * Orchestrates PageState capture, schema validation, and (on the benchmark
 * page) the ground-truth accuracy benchmark.
 * No external network requests. No PII sanitization (that is Member 2's job).
 */

"use strict";

(function () {

  // Detect whether we are on the benchmark test page.
  // We check for the presence of a known benchmark element rather than
  // matching the URL, so it works with both file:// and http://.
  function isBenchmarkPage() {
    return !!document.getElementById("el-h1");
  }

  function run() {
    const pageState = window.__pageStateCapture();
    const schemaErrors = window.__pageStateValidate(pageState);

    // -----------------------------------------------------------------------
    // Debug output
    // -----------------------------------------------------------------------
    console.group("=== PRIVACY-PRESERVING BROWSER AGENT ===");
    console.log("PAGE STATE");
    console.log(JSON.stringify(pageState, null, 2));
    console.groupEnd();

    // -----------------------------------------------------------------------
    // Schema validation  (always runs, clearly labelled)
    // -----------------------------------------------------------------------
    if (schemaErrors.length === 0) {
      console.log("[Schema validation] ✅ PASSED");
    } else {
      console.error("[Schema validation] ❌ FAILED:");
      schemaErrors.forEach((e) => console.error("  •", e));
    }

    // -----------------------------------------------------------------------
    // Registry debug
    // -----------------------------------------------------------------------
    console.group("[PageState] Element Registry");
    window.__elementRegistry.forEach((ref, id) => {
      const el = ref.deref ? ref.deref() : ref; // WeakRef (Day 2) or raw Element (Day 1)
      if (!el || !el.isConnected) return;        // skip stale / detached nodes
      const tag = el.tagName.toUpperCase();
      const label =
        el.getAttribute("aria-label") ||
        el.getAttribute("placeholder") ||
        el.textContent.trim().slice(0, 40) ||
        "(no label)";
      console.log(`${id} → ${tag} "${label}"`);
    });
    console.groupEnd();

    // -----------------------------------------------------------------------
    // Ground-truth benchmark  (only on the benchmark test page)
    // -----------------------------------------------------------------------
    if (!isBenchmarkPage()) return;

    if (typeof window.__runBenchmark === "function") {
      console.log("[Perception benchmark] Running...");
      window.__runBenchmark(pageState);
    } else {
      console.error("[Perception benchmark] __runBenchmark not defined. Check that benchmark.js is loaded as a content script.");
    }
  }

  if (document.readyState === "complete" || document.readyState === "interactive") {
    run();
  } else {
    document.addEventListener("DOMContentLoaded", run, { once: true });
  }

})();
