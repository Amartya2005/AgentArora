/**
 * diff-test.js  — TEMPORARY, verification only
 *
 * Runs in the MV3 isolated world (same world as page-state.js) because it is
 * loaded as a content_script entry.  Calls window.__pageStateCapture()
 * directly — no DevTools console, no main-world injection needed.
 *
 * Sequence:
 *   C1 — first capture (cold start)
 *   C2 — second capture, no DOM changes
 *   C3 — mutate #el-aria-label → "Full Name Updated", capture
 *   C4 — restore #el-aria-label → "Full Name", capture
 *   C5 — final capture, no changes
 *
 * Results are printed to the console under the label [DiffTest].
 * This file must be removed from manifest.json after verification.
 */

"use strict";

(function () {

  // Only run on the benchmark page so it does not fire on every site.
  if (!document.getElementById("el-h1")) return;

  function capture(label) {
    const ps = window.__pageStateCapture();
    // The diff line is already logged by capturePageState() itself.
    // We add a labelled marker so the five captures are easy to identify.
    console.log(`[DiffTest] ── ${label} ──`);
    return ps;
  }

  function mutate(value) {
    const el = document.getElementById("el-aria-label");
    if (el) el.setAttribute("aria-label", value);
  }

  // Small async wrapper so each capture gets its own microtask tick,
  // ensuring the console lines appear in order.
  async function runDiffTest() {
    console.log("\n[DiffTest] ════ DIFF CHANGED DETECTION TEST ════");

    // C1 — cold start
    capture("C1: first capture (cold start)");
    await new Promise(r => setTimeout(r, 50));

    // C2 — no DOM changes
    capture("C2: second capture, no changes");
    await new Promise(r => setTimeout(r, 50));

    // C3 — mutate label
    mutate("Full Name Updated");
    capture("C3: after aria-label → 'Full Name Updated'");
    await new Promise(r => setTimeout(r, 50));

    // C4 — restore label
    mutate("Full Name");
    capture("C4: after aria-label restored → 'Full Name'");
    await new Promise(r => setTimeout(r, 50));

    // C5 — final unchanged
    capture("C5: final capture, no changes");

    console.log("[DiffTest] ════ TEST COMPLETE ════\n");

    // Self-remove so it does not pollute window
    delete window.__diffTest;
  }

  // Run after a short delay to ensure content.js has already fired its
  // initial capture (which seeds _nodeFingerprint for C1 baseline).
  // content.js runs at document_idle; this script also runs at document_idle
  // but is listed after content.js in the js array, so it executes after.
  // The 200ms delay gives content.js time to complete its synchronous run().
  setTimeout(runDiffTest, 200);

})();
