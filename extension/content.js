/**
 * content.js
 * Browser perception bootstrap and schema gate.
 *
 * SECURITY:
 * - Raw PageState is never written to the console.
 * - Element registry contents are never written to the console.
 * - PII sanitization remains the responsibility of the privacy engine.
 */

"use strict";

(function () {
  if (window.__captureFreshPageState) return;

  function capturePageState() {
    const pageState = window.__pageStateCapture();
    const schemaErrors = window.__pageStateValidate(pageState);

    // Do not log pageState, element labels, values, visible text, or registry
    // contents. The browser perception layer may contain raw sensitive data.
    if (schemaErrors.length !== 0) {
      schemaErrors.forEach((error) => {
        console.error("[PageState] schema validation failed:", error);
      });
    }
    return pageState;
  }

  // This remains browser-local. A downstream privacy integration may request a
  // capture, but this script never sends raw PageState to the reasoning agent.
  window.__captureFreshPageState = capturePageState;

  if (document.readyState === "complete" || document.readyState === "interactive") {
    capturePageState();
  } else {
    document.addEventListener("DOMContentLoaded", capturePageState, { once: true });
  }
})();
