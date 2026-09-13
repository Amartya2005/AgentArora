/**
 * page-state.js
 * Member 1 — Browser Perception Layer
 * Produces a PageState conforming exactly to page-state.schema.json v1.0
 *
 * SECURITY RULES (enforced here):
 *   - Password input values are NEVER captured.
 *   - No external network requests are made.
 *   - No cookies, tokens, or credentials are captured.
 */

"use strict";

// ---------------------------------------------------------------------------
// Element Registry  (EL_xxx → DOM node, in-memory only)
// ---------------------------------------------------------------------------
const _registry = new Map(); // Map<string, Element>
let _counter = 0;

function _nextId() {
  _counter += 1;
  // Pad to at least 3 digits; supports up to 999999 per schema ^EL_[0-9]{3,6}$
  const padded = String(_counter).padStart(3, "0").slice(0, 6);
  return "EL_" + padded;
}

function _register(el) {
  const id = _nextId();
  _registry.set(id, el);
  return id;
}

/** Reset registry between captures (allows re-capture on same page). */
function _resetRegistry() {
  _registry.clear();
  _counter = 0;
}

// ---------------------------------------------------------------------------
// Visibility
// ---------------------------------------------------------------------------
function _isVisible(el) {
  if (!el.isConnected) return false;
  const rect = el.getBoundingClientRect();
  if (rect.width === 0 && rect.height === 0) return false;
  const style = window.getComputedStyle(el);
  if (style.display === "none") return false;
  if (style.visibility === "hidden") return false;
  if (style.opacity === "0") return false;
  return true;
}

// ---------------------------------------------------------------------------
// Enabled state
// ---------------------------------------------------------------------------
function _isEnabled(el) {
  // Native disabled property covers input/button/select/textarea/fieldset
  if ("disabled" in el) return !el.disabled;
  // aria-disabled
  if (el.getAttribute("aria-disabled") === "true") return false;
  return true;
}

// ---------------------------------------------------------------------------
// Bounds
// ---------------------------------------------------------------------------
function _bounds(el) {
  const r = el.getBoundingClientRect();
  return {
    x: Math.round(r.left),
    y: Math.round(r.top),
    width: Math.round(r.width),
    height: Math.round(r.height),
  };
}

// ---------------------------------------------------------------------------
// Label resolution
// ---------------------------------------------------------------------------
function _label(el) {
  // 1. aria-label
  const ariaLabel = el.getAttribute("aria-label");
  if (ariaLabel && ariaLabel.trim()) return ariaLabel.trim().slice(0, 500);

  // 2. aria-labelledby
  const labelledBy = el.getAttribute("aria-labelledby");
  if (labelledBy) {
    const text = labelledBy
      .split(/\s+/)
      .map((id) => document.getElementById(id)?.textContent?.trim() ?? "")
      .join(" ")
      .trim();
    if (text) return text.slice(0, 500);
  }

  // 3. <label for="id"> or wrapping <label>
  if (el.id) {
    const forLabel = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
    if (forLabel) return forLabel.textContent.trim().slice(0, 500);
  }
  const parentLabel = el.closest("label");
  if (parentLabel) {
    // Exclude the element's own text from the label text
    const clone = parentLabel.cloneNode(true);
    clone.querySelectorAll("input,select,textarea").forEach((n) => n.remove());
    const t = clone.textContent.trim();
    if (t) return t.slice(0, 500);
  }

  // 4. placeholder as fallback label
  const placeholder = el.getAttribute("placeholder");
  if (placeholder && placeholder.trim()) return placeholder.trim().slice(0, 500);

  // 5. title
  const title = el.getAttribute("title");
  if (title && title.trim()) return title.trim().slice(0, 500);

  return "";
}

// ---------------------------------------------------------------------------
// Role resolution
// ---------------------------------------------------------------------------
function _role(el) {
  const explicit = el.getAttribute("role");
  if (explicit && explicit.trim()) return explicit.trim().slice(0, 80);

  const tag = el.tagName.toLowerCase();
  const type = (el.getAttribute("type") || "").toLowerCase();

  const map = {
    button: "button",
    a: "link",
    select: "combobox",
    textarea: "textbox",
    h1: "heading", h2: "heading", h3: "heading",
    h4: "heading", h5: "heading", h6: "heading",
    label: "label",
    img: "img",
    nav: "navigation",
    main: "main",
    header: "banner",
    footer: "contentinfo",
    form: "form",
  };

  if (tag === "input") {
    if (type === "checkbox") return "checkbox";
    if (type === "radio") return "radio";
    if (type === "submit" || type === "button" || type === "reset") return "button";
    if (type === "range") return "slider";
    return "textbox";
  }

  return map[tag] || tag;
}

// ---------------------------------------------------------------------------
// Text content (normalised, no raw HTML)
// ---------------------------------------------------------------------------
function _text(el) {
  // For inputs, use value only if not password; for others use textContent
  const tag = el.tagName.toLowerCase();
  const type = (el.getAttribute("type") || "").toLowerCase();

  if (tag === "input") {
    if (type === "password") return ""; // NEVER capture password value as text
    // For non-password inputs, text is empty (value is separate)
    return "";
  }
  if (tag === "select") {
    const opt = el.options[el.selectedIndex];
    return opt ? opt.text.trim().slice(0, 2000) : "";
  }
  if (tag === "textarea") return ""; // value handled separately

  const raw = el.textContent || el.innerText || "";
  return raw.replace(/\s+/g, " ").trim().slice(0, 2000);
}

// ---------------------------------------------------------------------------
// Value (only for non-password inputs/textareas, for Member 2 privacy scan)
// ---------------------------------------------------------------------------
function _value(el) {
  const tag = el.tagName.toLowerCase();
  const type = (el.getAttribute("type") || "").toLowerCase();

  // HARD RULE: never capture password values
  if (type === "password") return undefined;

  if (tag === "input" || tag === "textarea") {
    const v = el.value;
    if (v === undefined || v === null || v === "") return undefined;
    return String(v).slice(0, 2000);
  }
  return undefined;
}

// ---------------------------------------------------------------------------
// Element type field
// ---------------------------------------------------------------------------
function _type(el) {
  const tag = el.tagName.toLowerCase();
  if (tag === "input") {
    return (el.getAttribute("type") || "text").toLowerCase().slice(0, 80);
  }
  if (tag === "a") return "link";
  if (tag === "button") return "button";
  if (tag === "select") return "select";
  if (tag === "textarea") return "textarea";
  if (/^h[1-6]$/.test(tag)) return tag;
  return tag.slice(0, 80);
}

// ---------------------------------------------------------------------------
// Element selector — which elements to extract
// ---------------------------------------------------------------------------
const SELECTOR =
  "button, a[href], input:not([type='hidden']), textarea, select, " +
  "h1, h2, h3, h4, h5, h6, label, " +
  "[role='button'], [role='link'], [role='checkbox'], [role='radio'], " +
  "[role='textbox'], [role='combobox'], [role='menuitem'], [role='tab']";

// ---------------------------------------------------------------------------
// PageState ID generator
// ---------------------------------------------------------------------------
function _pageStateId() {
  // Pattern: ^PS_[A-Za-z0-9_-]{6,64}$
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let id = "PS_";
  for (let i = 0; i < 10; i++) {
    id += chars[Math.floor(Math.random() * chars.length)];
  }
  return id;
}

// ---------------------------------------------------------------------------
// Visible text (raw, for Member 2)
// ---------------------------------------------------------------------------
function _visibleText() {
  // Walk text nodes that are visible; skip script/style
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode(node) {
        const p = node.parentElement;
        if (!p) return NodeFilter.FILTER_REJECT;
        const tag = p.tagName.toLowerCase();
        if (tag === "script" || tag === "style" || tag === "noscript") {
          return NodeFilter.FILTER_REJECT;
        }
        const style = window.getComputedStyle(p);
        if (style.display === "none" || style.visibility === "hidden") {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      },
    }
  );

  const parts = [];
  let node;
  while ((node = walker.nextNode())) {
    const t = node.textContent.replace(/\s+/g, " ").trim();
    if (t) parts.push(t);
  }
  return parts.join(" ").slice(0, 20000);
}

// ---------------------------------------------------------------------------
// Deduplication set (cleared each capture)
// ---------------------------------------------------------------------------
const _seen = new Set();

// ---------------------------------------------------------------------------
// Main capture function
// ---------------------------------------------------------------------------
function capturePageState() {
  const t0 = performance.now();
  _resetRegistry();

  const nodes = document.querySelectorAll(SELECTOR);
  const elements = [];

  nodes.forEach((el) => {
    // Skip duplicates (e.g. a button matched by tag and by role)
    // We use a WeakSet to deduplicate
    if (_seen.has(el)) return;
    _seen.add(el);

    const visible = _isVisible(el);
    const enabled = _isEnabled(el);
    const id = _register(el);

    const entry = {
      element_id: id,
      role: _role(el),
      visible,
      enabled,
    };

    const type = _type(el);
    if (type) entry.type = type;

    const label = _label(el);
    if (label !== "") entry.label = label;

    const text = _text(el);
    if (text !== "") entry.text = text;

    const value = _value(el);
    if (value !== undefined) entry.value = value;

    if (visible) entry.bounds = _bounds(el);

    elements.push(entry);
  });

  _seen.clear();

  const pageState = {
    schema_version: "1.0",
    page_state_id: _pageStateId(),
    captured_at: new Date().toISOString(),
    url: location.href.slice(0, 2048),
    title: (document.title || "").slice(0, 300),
    visible_text: _visibleText(),
    elements: elements.slice(0, 500),
  };

  const elapsed = (performance.now() - t0).toFixed(1);
  console.log(`[PageState] captured ${elements.length} elements in ${elapsed}ms`);

  return pageState;
}

// ---------------------------------------------------------------------------
// Inline schema validator (structural only — no external fetch)
// Validates the PageState we just built against the frozen contract rules.
// ---------------------------------------------------------------------------
function validatePageState(ps) {
  const errors = [];

  function check(cond, msg) {
    if (!cond) errors.push(msg);
  }

  check(ps.schema_version === "1.0", "schema_version must be '1.0'");
  check(/^PS_[A-Za-z0-9_-]{6,64}$/.test(ps.page_state_id), "page_state_id pattern mismatch");
  check(typeof ps.captured_at === "string" && !isNaN(Date.parse(ps.captured_at)), "captured_at invalid");
  check(typeof ps.url === "string" && ps.url.length >= 1 && ps.url.length <= 2048, "url invalid");
  check(typeof ps.title === "string" && ps.title.length <= 300, "title invalid");
  check(typeof ps.visible_text === "string" && ps.visible_text.length <= 20000, "visible_text invalid");
  check(Array.isArray(ps.elements) && ps.elements.length <= 500, "elements invalid");

  const allowedTopKeys = new Set([
    "schema_version","page_state_id","captured_at","url","title",
    "visible_text","elements","accessibility_snapshot","visual_summary","error"
  ]);
  Object.keys(ps).forEach((k) => check(allowedTopKeys.has(k), `unexpected top-level key: ${k}`));

  const allowedElKeys = new Set([
    "element_id","role","type","label","text","value","visible","enabled","bounds"
  ]);

  ps.elements.forEach((el, i) => {
    const pfx = `elements[${i}]`;
    check(/^EL_[0-9]{3,6}$/.test(el.element_id), `${pfx}.element_id pattern mismatch: ${el.element_id}`);
    check(typeof el.role === "string" && el.role.length >= 1 && el.role.length <= 80, `${pfx}.role invalid`);
    check(typeof el.visible === "boolean", `${pfx}.visible must be boolean`);
    check(typeof el.enabled === "boolean", `${pfx}.enabled must be boolean`);
    if (el.type !== undefined) check(typeof el.type === "string" && el.type.length <= 80, `${pfx}.type invalid`);
    if (el.label !== undefined) check(typeof el.label === "string" && el.label.length <= 500, `${pfx}.label invalid`);
    if (el.text !== undefined) check(typeof el.text === "string" && el.text.length <= 2000, `${pfx}.text invalid`);
    if (el.value !== undefined) check((typeof el.value === "string" || el.value === null) && (el.value === null || el.value.length <= 2000), `${pfx}.value invalid`);
    if (el.bounds !== undefined) {
      const b = el.bounds;
      check(typeof b.x === "number" && typeof b.y === "number" && typeof b.width === "number" && typeof b.height === "number", `${pfx}.bounds fields must be numbers`);
      check(b.width >= 0 && b.height >= 0, `${pfx}.bounds width/height must be >= 0`);
      Object.keys(b).forEach((k) => check(["x","y","width","height"].includes(k), `${pfx}.bounds unexpected key: ${k}`));
    }
    Object.keys(el).forEach((k) => check(allowedElKeys.has(k), `${pfx} unexpected key: ${k}`));
  });

  return errors;
}

// Expose for content.js
window.__pageStateCapture = capturePageState;
window.__pageStateValidate = validatePageState;
window.__elementRegistry = _registry;
