/**
 * content.js
 * Browser perception bootstrap and schema gate.
 *
 * SECURITY:
 * - Raw PageState is never written to the console.
 * - Element registry contents are never written to the console.
 * - Raw PageState is sent only to the localhost bridge so Python can apply
 *   the PrivacyEngine before any reasoning step.
 */

"use strict";

(function () {
  if (window.__captureFreshPageState) return;

  function publishPageState(pageState) {
    try {
      chrome.runtime.sendMessage({
        type: "PAGE_STATE",
        page_state: pageState,
      }).catch(() => {});
    } catch (_error) {
      // The perception layer must remain usable even if the bridge is offline.
      // Do not expose raw PageState in diagnostics.
    }
  }

  function capturePageState() {
    const pageState = window.__pageStateCapture();
    const schemaErrors = window.__pageStateValidate(pageState);

    // Do not log pageState, element labels, values, visible text, or registry
    // contents. The browser perception layer may contain raw sensitive data.
    if (schemaErrors.length !== 0) {
      schemaErrors.forEach((error) => {
        console.error("[PageState] schema validation failed:", error);
      });
      return pageState;
    }

    publishPageState(pageState);
    return pageState;
  }

  window.__captureFreshPageState = capturePageState;

  if (document.readyState === "complete" || document.readyState === "interactive") {
    capturePageState();
  } else {
    document.addEventListener("DOMContentLoaded", capturePageState, { once: true });
  }
})();
