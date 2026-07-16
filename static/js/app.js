/* =====================================================================
   Kash – Core JS (theme, locale, form helpers)
   ===================================================================== */

(function () {
  "use strict";

  // ── Theme toggle ─────────────────────────────────────────────────────
  var saved = null;
  try { saved = localStorage.getItem("kash-theme"); } catch (_) {}

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    var light = document.getElementById("theme-icon-light");
    var dark = document.getElementById("theme-icon-dark");
    if (light && dark) {
      light.classList.toggle("hidden", theme === "dark");
      dark.classList.toggle("hidden", theme === "light");
    }
  }

  // Detect OS preference if no saved theme
  var theme = saved || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  applyTheme(theme);

  var toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      theme = theme === "light" ? "dark" : "light";
      applyTheme(theme);
      try { localStorage.setItem("kash-theme", theme); } catch (_) {}
      // Persist to server
      if (window.KASH && window.KASH.user) {
        fetch("/preferences", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: "theme=" + encodeURIComponent(theme) + "&locale=" + encodeURIComponent(window.KASH.locale || "es"),
        });
      }
    });
  }

  // ── Locale toggle ────────────────────────────────────────────────────
  var localeBtn = document.getElementById("locale-toggle");
  if (localeBtn) {
    localeBtn.addEventListener("click", function () {
      var current = window.KASH ? window.KASH.locale : "es";
      var next = current === "es" ? "en" : "es";
      try { localStorage.setItem("kash-locale", next); } catch (_) {}
      // Persist and reload to get new strings from server
      if (window.KASH && window.KASH.user) {
        fetch("/preferences", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: "locale=" + encodeURIComponent(next) + "&theme=" + encodeURIComponent(window.KASH.theme || "light"),
        }).then(function () {
          window.location.reload();
        });
      } else {
        window.location.reload();
      }
    });
  }

  // ── Form helpers (date+time → ISO datetime) ──────────────────────────
  function setupForms() {
    var forms = document.querySelectorAll("form");
    forms.forEach(function (form) {
      var dateEl = form.querySelector('input[name="occurred_at_date"]');
      var timeEl = form.querySelector('input[name="occurred_at_time"]');
      var dtEl = form.querySelector('input[name="occurred_at"]');
      if (dateEl && timeEl && dtEl) {
        form.addEventListener("submit", function () {
          var d = dateEl.value || new Date().toISOString().slice(0, 10);
          var t = timeEl.value || "12:00";
          dtEl.value = d + "T" + t + ":00";
        });
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupForms);
  } else {
    setupForms();
  }

  // ── Sheet form: close on successful submit ──────────────────────────
  function setupSheets() {
    var sheets = document.querySelectorAll(".sheet");
    sheets.forEach(function (sheet) {
      var form = sheet.querySelector("form");
      if (form) {
        form.addEventListener("submit", function () {
          // Sheet will close via redirect
        });
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupSheets);
  } else {
    setupSheets();
  }
})();

/* ── Method pill selector (global, used in inline onclick) ──────────── */
function selectMethod(el) {
  var parent = el.closest(".method-pills");
  if (!parent) parent = el.parentElement;
  parent.querySelectorAll(".method-pill").forEach(function (b) {
    b.classList.remove("active");
  });
  el.classList.add("active");
  // Find the hidden input and update it
  var form = el.closest("form");
  if (form) {
    var input = form.querySelector('input[name="payment_method"]');
    if (input) input.value = el.dataset.method;
  }
}
