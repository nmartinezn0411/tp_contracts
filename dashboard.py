from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json
import mimetypes
import os

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
HOST = "0.0.0.0"
PORT = 8001
DATA_FILE = ROOT / "src" / "data" / "output" / "billing_validation.json"

USERNAME_APP = os.getenv("USERNAME_APP")
PASSWORD_APP = os.getenv("PASSWORD_APP")


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def is_logged_in(self):
        cookie = self.headers.get("Cookie", "")
        return "auth=true" in cookie

    def redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def send_html(self, content, status=200):
        payload = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def serve_login_page(self, error=False):
        error_msg = (
            "<p class='login-error'>Credenciales invalidas. Intenta nuevamente.</p>"
            if error
            else ""
        )
        self.send_html(
            f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Acceso al Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4efe7;
      --panel: rgba(255, 252, 247, 0.92);
      --ink: #1f2937;
      --muted: #6b7280;
      --accent: #c26a2d;
      --accent-dark: #8c4517;
      --border: rgba(107, 114, 128, 0.18);
      --danger: #b42318;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(194, 106, 45, 0.25), transparent 30%),
        radial-gradient(circle at bottom right, rgba(15, 118, 110, 0.14), transparent 32%),
        linear-gradient(135deg, #f9f4ec 0%, #efe4d4 48%, #f6efe6 100%);
      padding: 24px;
    }}
    .login-shell {{
      width: min(960px, 100%);
      display: grid;
      grid-template-columns: 1.2fr 0.9fr;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 28px;
      overflow: hidden;
      box-shadow: 0 24px 90px rgba(31, 41, 55, 0.16);
      backdrop-filter: blur(18px);
    }}
    .login-copy {{
      padding: 56px;
      background:
        linear-gradient(160deg, rgba(255,255,255,0.58), rgba(255,255,255,0.12)),
        linear-gradient(140deg, #12343b, #28565f 58%, #3d706c);
      color: #f8fafc;
    }}
    .eyebrow {{
      display: inline-flex;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(255,255,255,0.14);
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 18px 0 14px;
      font-size: clamp(2rem, 4vw, 3.4rem);
      line-height: 1;
    }}
    .lead {{
      margin: 0 0 24px;
      font-size: 1.05rem;
      line-height: 1.65;
      color: rgba(248, 250, 252, 0.86);
    }}
    .feature {{
      margin: 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 12px;
    }}
    .feature li {{
      padding: 14px 16px;
      border-radius: 16px;
      background: rgba(255,255,255,0.12);
      border: 1px solid rgba(255,255,255,0.1);
    }}
    .login-card {{
      padding: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 252, 247, 0.96);
    }}
    .login-panel {{
      width: min(360px, 100%);
    }}
    h2 {{
      margin: 0 0 10px;
      font-size: 1.8rem;
    }}
    .subtle {{
      margin: 0 0 24px;
      color: var(--muted);
      line-height: 1.55;
    }}
    label {{
      display: block;
      margin-bottom: 8px;
      font-weight: 600;
    }}
    input {{
      width: 100%;
      margin-bottom: 16px;
      padding: 14px 16px;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: #fff;
      font-size: 1rem;
    }}
    input:focus {{
      outline: 2px solid rgba(194, 106, 45, 0.28);
      border-color: rgba(194, 106, 45, 0.6);
    }}
    button {{
      width: 100%;
      padding: 14px 18px;
      border: none;
      border-radius: 14px;
      background: linear-gradient(135deg, var(--accent), var(--accent-dark));
      color: white;
      font-size: 1rem;
      font-weight: 700;
      cursor: pointer;
    }}
    .login-error {{
      color: var(--danger);
      background: rgba(180, 35, 24, 0.08);
      border: 1px solid rgba(180, 35, 24, 0.14);
      padding: 12px 14px;
      border-radius: 12px;
      margin-bottom: 18px;
    }}
    @media (max-width: 820px) {{
      .login-shell {{
        grid-template-columns: 1fr;
      }}
      .login-copy, .login-card {{
        padding: 28px;
      }}
    }}
  </style>
</head>
<body>
  <main class="login-shell">
    <section class="login-copy">
      <span class="eyebrow">Control Preventivo de Facturacion</span>
      <h1>Detecta discrepancias antes de enviar la factura al cliente.</h1>
      <p class="lead">
        Este dashboard resume errores de horas, tarifas, sobrefacturacion y
        hallazgos explicados por IA para apoyar revisiones internas antes del envio final.
      </p>
      <ul class="feature">
        <li>Prioriza casos criticos y cuantifica el impacto economico.</li>
        <li>Permite revisar cada incidente con detalle y recomendaciones accionables.</li>
        <li>Ayuda a prevenir reclamos, ajustes manuales y perdida de confianza del cliente.</li>
      </ul>
    </section>
    <section class="login-card">
      <div class="login-panel">
        <h2>Iniciar sesion</h2>
        <p class="subtle">Accede al dashboard protegido para revisar los hallazgos de validacion.</p>
        {error_msg}
        <form method="POST" action="/login">
          <label for="username">Usuario</label>
          <input id="username" name="username" placeholder="Ingresa tu usuario" autocomplete="username" />
          <label for="password">Contrasena</label>
          <input id="password" name="password" type="password" placeholder="Ingresa tu contrasena" autocomplete="current-password" />
          <button type="submit">Entrar al dashboard</button>
        </form>
      </div>
    </section>
  </main>
</body>
</html>"""
        )

    def serve_json_data(self):
        if not DATA_FILE.exists():
            self.send_error(404, "No se encontro el archivo de validacion.")
            return

        payload = DATA_FILE.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def serve_dashboard_asset(self, relative_path):
        asset_path = ROOT / "dashboard" / relative_path
        if asset_path.is_dir():
            asset_path = asset_path / "index.html"

        if not asset_path.exists() or not asset_path.is_file():
            self.send_error(404, "Recurso no encontrado.")
            return

        content_type, _ = mimetypes.guess_type(str(asset_path))
        payload = asset_path.read_bytes()
        self.send_response(200)
        self.send_header(
            "Content-Type",
            f"{content_type or 'application/octet-stream'}; charset=utf-8",
        )
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self.redirect("/dashboard/" if self.is_logged_in() else "/login")
            return

        if path == "/login":
            if self.is_logged_in():
                self.redirect("/dashboard/")
                return
            self.serve_login_page()
            return

        if path == "/logout":
            self.send_response(302)
            self.send_header("Location", "/login")
            self.send_header("Set-Cookie", "auth=false; Path=/; Max-Age=0; HttpOnly; SameSite=Lax")
            self.end_headers()
            return

        if path.startswith("/api/"):
            if not self.is_logged_in():
                self.send_error(401, "No autorizado.")
                return
            if path == "/api/billing-validation":
                self.serve_json_data()
                return
            self.send_error(404, "Ruta API no encontrada.")
            return

        if path.startswith("/dashboard"):
            if not self.is_logged_in():
                self.redirect("/login")
                return

            relative_path = path.removeprefix("/dashboard").lstrip("/") or "index.html"
            self.serve_dashboard_asset(relative_path)
            return

        self.send_error(404, "Ruta no encontrada.")

    def do_POST(self):
        if self.path != "/login":
            self.send_error(404, "Ruta no encontrada.")
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        data = parse_qs(body)

        username = data.get("username", [""])[0]
        password = data.get("password", [""])[0]

        if username == USERNAME_APP and password == PASSWORD_APP:
            self.send_response(302)
            self.send_header("Location", "/dashboard/")
            self.send_header("Set-Cookie", "auth=true; Path=/; HttpOnly; SameSite=Lax")
            self.end_headers()
            return

        self.serve_login_page(error=True)


if __name__ == "__main__":
    os.chdir(ROOT)
    server = ThreadingHTTPServer((HOST, PORT), DashboardHandler)
    print(f"Dashboard disponible en http://localhost:{PORT}/dashboard/")
    server.serve_forever()
