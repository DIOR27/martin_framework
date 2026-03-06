"""
Martin — Example App (Vite-inspired glassmorphism)
Run: python example_app.py
"""

import sys, http.server, webbrowser, threading

sys.path.insert(0, "..")

HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Martin — Python Web Framework</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root { --accent: #818cf8; --accent2: #34d399; --bg: #060818; }
    body { font-family: 'Syne', sans-serif; background: var(--bg); color: #f1f5f9; min-height: 100vh; overflow-x: hidden; }

    .bg-mesh {
      position: fixed; inset: 0; z-index: 0; pointer-events: none;
      background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(99,102,241,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 80%, rgba(52,211,153,0.12) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 50% 50%, rgba(139,92,246,0.08) 0%, transparent 50%),
        #060818;
    }
    .orb { position: fixed; border-radius: 50%; filter: blur(80px); pointer-events: none; z-index: 0; animation: float 8s ease-in-out infinite; }
    .orb-1 { width:500px;height:500px;top:-100px;left:-100px;background:rgba(99,102,241,0.12);animation-delay:0s; }
    .orb-2 { width:400px;height:400px;bottom:-80px;right:-80px;background:rgba(52,211,153,0.1);animation-delay:-3s; }
    .orb-3 { width:300px;height:300px;top:40%;left:50%;background:rgba(139,92,246,0.08);animation-delay:-5s; }
    @keyframes float { 0%,100%{transform:translate(0,0) scale(1)} 33%{transform:translate(30px,-20px) scale(1.05)} 66%{transform:translate(-20px,15px) scale(0.97)} }

    .noise { position:fixed;inset:0;z-index:0;pointer-events:none;opacity:0.025;
      background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
      background-size:200px; }

    .content { position: relative; z-index: 1; }

    nav { position:fixed;top:0;left:0;right:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:16px 48px;background:rgba(6,8,24,0.6);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border-bottom:1px solid rgba(255,255,255,0.06); }
    .nav-logo { font-size:22px;font-weight:800;letter-spacing:-0.5px;background:linear-gradient(135deg,#818cf8,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent; }
    .nav-links { display:flex;gap:32px;align-items:center; }
    .nav-links a { color:rgba(203,213,225,0.7);text-decoration:none;font-size:14px;font-weight:500;transition:color 0.2s; }
    .nav-links a:hover { color:#f1f5f9; }
    .btn-nav { padding:8px 18px;border-radius:8px;font-size:13px;font-weight:600;background:rgba(129,140,248,0.15);border:1px solid rgba(129,140,248,0.35);color:#a5b4fc;cursor:pointer;transition:all 0.2s;text-decoration:none;font-family:'Syne',sans-serif; }
    .btn-nav:hover { background:rgba(129,140,248,0.25);border-color:rgba(129,140,248,0.6);color:#e0e7ff; }

    .hero { min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:120px 48px 80px;text-align:center; }

    .hero-badge { display:inline-flex;align-items:center;gap:8px;padding:6px 16px;border-radius:9999px;background:rgba(129,140,248,0.1);border:1px solid rgba(129,140,248,0.25);font-size:13px;color:#a5b4fc;font-weight:500;margin-bottom:32px;animation:fadeUp 0.6s ease both; }
    .hero-badge .dot { width:6px;height:6px;border-radius:50%;background:#34d399;animation:pulse 2s ease infinite; }
    @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(0.8)} }

    h1.hero-title { font-size:clamp(52px,8vw,96px);font-weight:800;letter-spacing:-3px;line-height:1;margin-bottom:24px;animation:fadeUp 0.6s 0.1s ease both; }
    .gradient-text { background:linear-gradient(135deg,#c7d2fe 0%,#818cf8 40%,#34d399 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent; }
    .hero-sub { font-size:clamp(16px,2vw,20px);color:rgba(148,163,184,0.9);max-width:540px;line-height:1.6;margin-bottom:48px;font-weight:400;animation:fadeUp 0.6s 0.2s ease both; }
    .hero-actions { display:flex;gap:12px;flex-wrap:wrap;justify-content:center;animation:fadeUp 0.6s 0.3s ease both; }

    .btn-primary { padding:14px 28px;border-radius:10px;font-size:15px;font-weight:700;background:linear-gradient(135deg,#6366f1,#818cf8);border:none;color:#fff;cursor:pointer;box-shadow:0 0 32px rgba(99,102,241,0.35);transition:all 0.2s;text-decoration:none;font-family:'Syne',sans-serif; }
    .btn-primary:hover { transform:translateY(-2px);box-shadow:0 0 48px rgba(99,102,241,0.5); }
    .btn-ghost { padding:14px 28px;border-radius:10px;font-size:15px;font-weight:600;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12);color:#cbd5e1;cursor:pointer;transition:all 0.2s;text-decoration:none;font-family:'Syne',sans-serif; }
    .btn-ghost:hover { background:rgba(255,255,255,0.1);border-color:rgba(255,255,255,0.2); }

    .hero-code { margin-top:64px;width:100%;max-width:600px;background:rgba(255,255,255,0.04);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.1);border-radius:16px;overflow:hidden;animation:fadeUp 0.6s 0.4s ease both;box-shadow:0 32px 64px rgba(0,0,0,0.4),inset 0 1px 0 rgba(255,255,255,0.1); }
    .code-titlebar { display:flex;align-items:center;gap:8px;padding:14px 20px;background:rgba(0,0,0,0.3);border-bottom:1px solid rgba(255,255,255,0.07); }
    .dot-r{width:12px;height:12px;border-radius:50%;background:#ff5f57}
    .dot-y{width:12px;height:12px;border-radius:50%;background:#febc2e}
    .dot-g{width:12px;height:12px;border-radius:50%;background:#28c840}
    .code-filename { font-size:13px;color:rgba(148,163,184,0.6);margin-left:8px;font-family:'DM Mono',monospace; }
    .code-body { padding:24px;font-family:'DM Mono',monospace;font-size:13px;line-height:1.8;color:#e2e8f0;text-align:left; }
    .kw{color:#818cf8} .fn{color:#34d399} .str{color:#fbbf24} .cm{color:rgba(148,163,184,0.45);font-style:italic} .cls{color:#f472b6}

    .stats-strip { display:flex;gap:1px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:16px;overflow:hidden;backdrop-filter:blur(20px);margin:0 48px 80px; }
    .stat { flex:1;padding:32px 24px;text-align:center;background:rgba(255,255,255,0.03);transition:background 0.2s; }
    .stat:hover { background:rgba(255,255,255,0.07); }
    .stat-val { font-size:36px;font-weight:800;letter-spacing:-1px;color:#f1f5f9; }
    .stat-label { font-size:13px;color:rgba(148,163,184,0.6);margin-top:4px; }

    section { padding:80px 48px;max-width:1100px;margin:0 auto; }
    .section-label { font-size:12px;font-weight:700;letter-spacing:3px;color:#6366f1;text-transform:uppercase;margin-bottom:12px; }
    .section-title { font-size:clamp(28px,4vw,42px);font-weight:800;letter-spacing:-1px;color:#f1f5f9;margin-bottom:16px; }
    .section-sub { font-size:16px;color:rgba(148,163,184,0.8);line-height:1.6;max-width:500px;margin-bottom:48px; }
    .features-grid { display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px; }

    .glass-card { background:rgba(255,255,255,0.05);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.12);border-radius:16px;padding:28px;transition:transform 0.2s,box-shadow 0.2s; }
    .glass-card:hover { transform:translateY(-4px);box-shadow:0 24px 48px rgba(0,0,0,0.3); }
    .feat-icon { width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:16px; }
    .feat-title { font-size:16px;font-weight:700;color:#f1f5f9;margin-bottom:8px; }
    .feat-desc { font-size:14px;color:rgba(203,213,225,0.75);line-height:1.6; }

    .widgets-demo { background:rgba(255,255,255,0.04);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.1);border-radius:20px;padding:32px;box-shadow:0 16px 48px rgba(0,0,0,0.3); }
    .widget-row { display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-bottom:16px; }
    .glass-input { flex:1;min-width:180px;padding:10px 14px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);border-radius:8px;color:#f1f5f9;font-size:14px;outline:none;font-family:'Syne',sans-serif;transition:border-color 0.2s,background 0.2s; }
    .glass-input:focus { border-color:rgba(129,140,248,0.5);background:rgba(255,255,255,0.09); }
    .glass-input::placeholder { color:rgba(148,163,184,0.5); }
    .glass-badge { display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:9999px;font-size:12px;font-weight:600; }

    footer { text-align:center;padding:48px;border-top:1px solid rgba(255,255,255,0.06);color:rgba(148,163,184,0.4);font-size:13px; }
    footer span { color:rgba(148,163,184,0.7); }

    @keyframes fadeUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
    ::-webkit-scrollbar{width:6px} ::-webkit-scrollbar-track{background:transparent} ::-webkit-scrollbar-thumb{background:rgba(129,140,248,0.3);border-radius:3px}
  </style>
</head>
<body>
<div class="bg-mesh"></div>
<div class="orb orb-1"></div><div class="orb orb-2"></div><div class="orb orb-3"></div>
<div class="noise"></div>
<div class="content">

  <nav>
    <div class="nav-logo">martin</div>
    <div class="nav-links">
      <a href="#">Docs</a><a href="#">Widgets</a><a href="#">Examples</a>
      <a href="#" class="btn-nav">GitHub →</a>
    </div>
  </nav>

  <div class="hero">
    <div class="hero-badge"><span class="dot"></span> v0.1.0 — ahora con glassmorphism</div>
    <h1 class="hero-title">Webs con Python,<br><span class="gradient-text">Flutter-style.</span></h1>
    <p class="hero-sub">Define interfaces con componentes Python puro. Sin HTML, sin CSS, sin JavaScript. Solo código limpio.</p>
    <div class="hero-actions">
      <a href="#" class="btn-primary">Empezar →</a>
      <a href="#" class="btn-ghost">Ver ejemplos</a>
    </div>
    <div class="hero-code">
      <div class="code-titlebar">
        <div class="dot-r"></div><div class="dot-y"></div><div class="dot-g"></div>
        <span class="code-filename">main.py</span>
      </div>
      <div class="code-body">
<span class="kw">from</span> martin <span class="kw">import</span> <span class="cls">App</span>, <span class="cls">Card</span>, <span class="cls">Column</span>, <span class="cls">Text</span>, <span class="cls">Image</span>
<span class="kw">from</span> martin <span class="kw">import</span> <span class="cls">Border</span>, <span class="cls">Padding</span>, <span class="cls">Shadow</span>

<span class="kw">def</span> <span class="fn">build</span>():
    <span class="kw">return</span> <span class="cls">Card</span>(
        style=[<span class="cls">Padding</span>(24), <span class="cls">Border</span>(radius=16), <span class="cls">Shadow</span>.lg()],
        children=[
            <span class="cls">Image</span>(<span class="str">"assets/logo.png"</span>, style=<span class="cls">Border</span>(radius=8)),
            <span class="cls">Text</span>(<span class="str">"Hola, Martin 👋"</span>),
        ]
    )

<span class="cls">App</span>(build=build, title=<span class="str">"Mi App"</span>).run() <span class="cm"># → localhost:309</span>
      </div>
    </div>
  </div>

  <div class="stats-strip">
    <div class="stat"><div class="stat-val gradient-text">0</div><div class="stat-label">líneas de HTML escritas</div></div>
    <div class="stat"><div class="stat-val gradient-text">0</div><div class="stat-label">ficheros CSS</div></div>
    <div class="stat"><div class="stat-val gradient-text">100%</div><div class="stat-label">Python puro</div></div>
    <div class="stat"><div class="stat-val gradient-text">309</div><div class="stat-label">puerto por defecto ♥</div></div>
  </div>

  <section>
    <p class="section-label">Por qué Martin</p>
    <h2 class="section-title">Todo lo que necesitas,<br>nada de lo que no.</h2>
    <p class="section-sub">Componentes expresivos, estilos componibles y servidor con hot reload incluido.</p>
    <div class="features-grid">
      <div class="glass-card">
        <div class="feat-icon" style="background:rgba(99,102,241,0.2);border:1px solid rgba(99,102,241,0.35)">🧩</div>
        <div class="feat-title">Widget tree</div>
        <div class="feat-desc">Compón interfaces anidando componentes Python, igual que Flutter. Nada de templates.</div>
      </div>
      <div class="glass-card">
        <div class="feat-icon" style="background:rgba(52,211,153,0.2);border:1px solid rgba(52,211,153,0.35)">🎨</div>
        <div class="feat-title">Estilos componibles</div>
        <div class="feat-desc">Border(), Padding(), Shadow(), CSS() — mezcla y combina. Escape hatch a CSS puro siempre disponible.</div>
      </div>
      <div class="glass-card">
        <div class="feat-icon" style="background:rgba(244,114,182,0.2);border:1px solid rgba(244,114,182,0.35)">⚡</div>
        <div class="feat-title">Hot reload</div>
        <div class="feat-desc">Guarda el fichero, el navegador se actualiza. Sin configuración, funciona desde el primer run().</div>
      </div>
      <div class="glass-card">
        <div class="feat-icon" style="background:rgba(251,191,36,0.2);border:1px solid rgba(251,191,36,0.35)">🔍</div>
        <div class="feat-title">Selects avanzados</div>
        <div class="feat-desc">Select con búsqueda integrada y MultiSelect tipo tags. Sin dependencias externas.</div>
      </div>
      <div class="glass-card">
        <div class="feat-icon" style="background:rgba(129,140,248,0.2);border:1px solid rgba(129,140,248,0.35)">📦</div>
        <div class="feat-title">Zero deps</div>
        <div class="feat-desc">Solo la stdlib de Python. Opcional: watchdog para hot reload. Nada más.</div>
      </div>
      <div class="glass-card">
        <div class="feat-icon" style="background:rgba(52,211,153,0.2);border:1px solid rgba(52,211,153,0.35)">🚀</div>
        <div class="feat-title">Export estático</div>
        <div class="feat-desc">app.export("index.html") genera un fichero HTML listo para Netlify, Vercel o donde quieras.</div>
      </div>
    </div>
  </section>

  <section style="padding-top:0">
    <p class="section-label">Componentes</p>
    <h2 class="section-title">Widgets listos<br>para usar.</h2>
    <div class="widgets-demo">
      <div class="widget-row">
        <span class="glass-badge" style="background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.3);color:#a5b4fc">🐍 Python</span>
        <span class="glass-badge" style="background:rgba(52,211,153,0.15);border:1px solid rgba(52,211,153,0.3);color:#6ee7b7">✅ Stable</span>
        <span class="glass-badge" style="background:rgba(251,191,36,0.15);border:1px solid rgba(251,191,36,0.3);color:#fde68a">⚡ Fast</span>
      </div>
      <div class="widget-row">
        <input class="glass-input" placeholder="TextField(placeholder=...)">
        <input class="glass-input" placeholder="type=email" type="email">
      </div>
      <div class="widget-row">
        <button class="btn-primary" style="font-size:14px;padding:10px 20px">Button("primary")</button>
        <button class="btn-ghost" style="font-size:14px;padding:10px 20px">Button("ghost")</button>
        <button style="padding:10px 20px;border-radius:8px;font-size:14px;font-weight:600;background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;cursor:pointer;font-family:'Syne',sans-serif">Button("danger")</button>
      </div>
      <div style="background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:16px 20px;font-family:'DM Mono',monospace;font-size:13px;line-height:1.7;color:#e2e8f0;margin-top:4px">
<span class="cls">Card</span>(<br>
&nbsp;&nbsp;style=[<span class="cls">Padding</span>(<span class="str">16</span>), <span class="cls">Border</span>(radius=<span class="str">12</span>), <span class="cls">Shadow</span>.md()],<br>
&nbsp;&nbsp;children=[<br>
&nbsp;&nbsp;&nbsp;&nbsp;<span class="cls">Image</span>(<span class="str">"foto.jpg"</span>, style=[<span class="cls">Border</span>(radius=<span class="str">8</span>), <span class="cls">CSS</span>(<span class="str">"object-fit:cover"</span>)]),<br>
&nbsp;&nbsp;&nbsp;&nbsp;<span class="cls">Text</span>(<span class="str">"Hola mundo"</span>, style=<span class="cls">TextStyle</span>(size=<span class="str">16</span>, weight=<span class="str">"bold"</span>)),<br>
&nbsp;&nbsp;]<br>
)
      </div>
    </div>
  </section>

  <footer>Hecho con 💜 en Python &nbsp;·&nbsp; Puerto <span>309</span> &nbsp;·&nbsp; 03 de septiembre</footer>
</div>
</body>
</html>"""

if __name__ == "__main__":
    port = 309

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            data = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *a):
            pass

    server = http.server.HTTPServer(("", port), Handler)
    print(f"🌐 Martin → http://localhost:{port}")
    threading.Timer(0.5, lambda: webbrowser.open(f"http://localhost:{port}")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋")
