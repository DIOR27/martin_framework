"""
Martin — Theme System
Modo oscuro, claro y automático via CSS variables + data-theme.

Uso:
    App(router=router, theme="dark").run()    # siempre oscuro
    App(router=router, theme="light").run()   # siempre claro
    App(router=router, theme="auto").run()    # sigue el sistema (default)
"""

# ── Variables CSS por tema ────────────────────────────────────────────────────

THEME_CSS = """
/* ── Tema claro ── */
[data-theme="light"], .theme-light {
  --bg:           #f8fafc;
  --bg-secondary: #f1f5f9;
  --surface:      #ffffff;
  --surface-2:    #f3f4f6;
  --border:       rgba(0,0,0,0.10);
  --border-input: #d1d5db;
  --text:         #0f172a;
  --text-muted:   #64748b;
  --text-placeholder: #94a3b8;
  --input-bg:     #ffffff;
  --input-color:  #0f172a;
  --accent:       #6366f1;
  --accent-hover: #4f46e5;
  --glass-bg:     rgba(255,255,255,0.65);
  --glass-border: rgba(0,0,0,0.08);
  --shadow:       0 2px 12px rgba(0,0,0,0.08);
  --nav-bg:       rgba(248,250,252,0.90);
  --nav-border:   rgba(0,0,0,0.07);
  --nav-text:     rgba(15,23,42,0.75);
  --dropdown-bg:  #ffffff;
}

/* ── Tema oscuro ── */
[data-theme="dark"], .theme-dark {
  --bg:           #060818;
  --bg-secondary: #0d1117;
  --surface:      rgba(255,255,255,0.05);
  --surface-2:    rgba(255,255,255,0.03);
  --border:       rgba(255,255,255,0.08);
  --border-input: rgba(255,255,255,0.15);
  --text:         #f1f5f9;
  --text-muted:   rgba(148,163,184,0.8);
  --text-placeholder: rgba(148,163,184,0.45);
  --input-bg:     rgba(255,255,255,0.06);
  --input-color:  #f1f5f9;
  --accent:       #818cf8;
  --accent-hover: #6366f1;
  --glass-bg:     rgba(255,255,255,0.07);
  --glass-border: rgba(255,255,255,0.12);
  --shadow:       0 4px 24px rgba(0,0,0,0.35);
  --nav-bg:       rgba(6,8,24,0.85);
  --nav-border:   rgba(255,255,255,0.08);
  --nav-text:     rgba(203,213,225,0.75);
  --dropdown-bg:  #1a1d2e;
}

/* ── Auto: usa preferencia del sistema ── */
@media (prefers-color-scheme: dark) {
  [data-theme="auto"] {
    --bg:           #060818;
    --bg-secondary: #0d1117;
    --surface:      rgba(255,255,255,0.05);
    --surface-2:    rgba(255,255,255,0.03);
    --border:       rgba(255,255,255,0.08);
    --border-input: rgba(255,255,255,0.15);
    --text:         #f1f5f9;
    --text-muted:   rgba(148,163,184,0.8);
    --text-placeholder: rgba(148,163,184,0.45);
    --input-bg:     rgba(255,255,255,0.06);
    --input-color:  #f1f5f9;
    --accent:       #818cf8;
    --accent-hover: #6366f1;
    --glass-bg:     rgba(255,255,255,0.07);
    --glass-border: rgba(255,255,255,0.12);
    --shadow:       0 4px 24px rgba(0,0,0,0.35);
    --nav-bg:       rgba(6,8,24,0.85);
    --nav-border:   rgba(255,255,255,0.08);
    --nav-text:     rgba(203,213,225,0.75);
  --dropdown-bg:  #1a1d2e;
  }
}
@media (prefers-color-scheme: light) {
  [data-theme="auto"] {
    --bg:           #f8fafc;
    --bg-secondary: #f1f5f9;
    --surface:      #ffffff;
    --surface-2:    #f3f4f6;
    --border:       rgba(0,0,0,0.10);
    --border-input: #d1d5db;
    --text:         #0f172a;
    --text-muted:   #64748b;
    --text-placeholder: #94a3b8;
    --input-bg:     #ffffff;
    --input-color:  #0f172a;
    --accent:       #6366f1;
    --accent-hover: #4f46e5;
    --glass-bg:     rgba(255,255,255,0.65);
    --glass-border: rgba(0,0,0,0.08);
    --shadow:       0 2px 12px rgba(0,0,0,0.08);
    --nav-bg:       rgba(248,250,252,0.90);
    --nav-border:   rgba(0,0,0,0.07);
    --nav-text:     rgba(15,23,42,0.75);
  --dropdown-bg:  #ffffff;
  }
}

/* ── Estilos base que usan las variables ── */
html, body {
  background: var(--bg);
  color: var(--text);
}

/* Inputs themed */
input:not([type="checkbox"]):not([type="radio"]),
select,
textarea {
  background:   var(--input-bg)     !important;
  color:        var(--input-color)  !important;
  border-color: var(--border-input) !important;
}
input::placeholder,
textarea::placeholder {
  color: var(--text-placeholder) !important;
}
input:focus:not([type="checkbox"]),
select:focus,
textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
  outline: none !important;
}

/* Select nativo */
select {
  background: var(--input-bg) !important;
  color: var(--input-color) !important;
}

/* Select custom dropdown */
.pw-select-drop {
  background: var(--surface) !important;
  border-color: var(--border-input) !important;
  backdrop-filter: blur(12px);
}
.pw-opt, .pw-mopt {
  color: var(--text) !important;
}
.pw-opt:hover, .pw-mopt:hover {
  background: var(--surface-2) !important;
}
"""

# ── Botón toggle de tema ──────────────────────────────────────────────────────

THEME_TOGGLE_JS = """
<script>
(function(){
  // Default: respect OS setting. User can override with the toggle button.
  var INITIAL = 'INITIAL_THEME';
  var stored  = localStorage.getItem('martin-theme');
  // If no stored preference, use the app default (usually 'auto')
  var active  = stored || INITIAL;

  function icon(t) {
    if (t === 'dark')  return '☀️';
    if (t === 'light') return '🌙';
    // auto — show which mode the OS is currently in
    var sysDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    return '🌗';
  }

  function setTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem('martin-theme', t);
    var btn = document.getElementById('_martin_theme_btn');
    if (btn) {
      btn.textContent = icon(t);
      btn.title = t === 'auto' ? 'Tema: automático (sistema)' :
                  t === 'dark' ? 'Tema: oscuro' : 'Tema: claro';
    }
  }

  function cycleTheme() {
    var cur = document.documentElement.getAttribute('data-theme') || 'auto';
    // cycle: auto → dark → light → auto
    setTheme(cur === 'auto' ? 'dark' : cur === 'dark' ? 'light' : 'auto');
  }

  // Listen for OS theme changes when in auto mode
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function() {
    var cur = document.documentElement.getAttribute('data-theme');
    if (cur === 'auto') setTheme('auto'); // re-apply to refresh icon
  });

  window._martinSetTheme   = setTheme;
  window._martinCycleTheme = cycleTheme;
  setTheme(active);
})();
</script>
"""

THEME_TOGGLE_BTN = """
<button id="_martin_theme_btn"
  onclick="window._martinCycleTheme()"
  title="Cambiar tema"
  style="position:fixed;bottom:20px;right:20px;z-index:9999;
         width:40px;height:40px;border-radius:50%;border:1px solid var(--border);
         background:var(--surface);color:var(--text);font-size:18px;
         cursor:pointer;display:flex;align-items:center;justify-content:center;
         backdrop-filter:blur(12px);box-shadow:var(--shadow);
         transition:transform 0.2s"
  onmouseover="this.style.transform='scale(1.1)'"
  onmouseout="this.style.transform='scale(1)'">
  🌗
</button>
"""
