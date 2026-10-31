"""Equipo SUPERVISADO: comparte la pantalla (solo con el código) y muestra un aviso permanente."""
import hmac, io, threading, time
import tkinter as tk
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from tkinter import messagebox, ttk

import mss
from PIL import Image

import comun, licencia


def capturar():
    with mss.mss() as s:  # una instancia por petición: mss no es seguro entre hilos
        raw = s.grab(s.monitors[0])  # todos los monitores
    img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
    img.thumbnail((1280, 1280))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=60)
    return buf.getvalue()


class Servidor(BaseHTTPRequestHandler):
    codigo, ultima, error = "", 0.0, ""

    def do_GET(self):
        if self.path != "/frame":
            return self.send_error(404)
        enviado = self.headers.get("X-Codigo", "").encode("utf-8", "ignore")
        if not hmac.compare_digest(enviado, self.codigo.encode()):
            time.sleep(1)  # frena la fuerza bruta
            return self.send_error(403)
        try:
            datos = capturar()
        except Exception as e:
            Servidor.error = f"No se pudo capturar la pantalla: {e}"
            return self.send_error(500)
        Servidor.error, Servidor.ultima = "", time.time()
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def log_message(self, *a):
        pass


def marca_agua(root):
    w = tk.Toplevel(root)
    w.overrideredirect(True)
    try:
        w.attributes("-alpha", 0.8)
    except tk.TclError:
        pass
    tk.Label(w, text="● Pantalla supervisada", bg="#b00020", fg="white",
             font=("Arial", 11, "bold"), padx=12, pady=5).pack()
    w.update_idletasks()
    w.geometry(f"+{w.winfo_screenwidth() - w.winfo_width() - 20}+{w.winfo_screenheight() - w.winfo_height() - 70}")

    def subir():  # mantenerla visible encima de todo
        w.lift()
        w.attributes("-topmost", True)
        w.after(3000, subir)
    subir()


def main():
    cfg = comun.cargar()
    if not cfg.get("codigo"):
        cfg["codigo"] = comun.nuevo_codigo()
        comun.guardar(cfg)
    Servidor.codigo = cfg["codigo"]
    root = tk.Tk()
    root.title("Pantalla supervisada")
    root.resizable(False, False)
    try:
        srv = ThreadingHTTPServer(("0.0.0.0", comun.PUERTO), Servidor)
    except OSError as e:
        root.withdraw()
        messagebox.showerror("No se pudo iniciar",
                             f"El puerto {comun.PUERTO} está ocupado (¿ya está abierta la aplicación?).\n\n{e}")
        return
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    f = ttk.Frame(root, padding=20)
    f.pack()
    ttk.Label(f, text="Este equipo está siendo supervisado", font=("Arial", 14, "bold")).pack()
    ttk.Label(f, text=f"Dirección: {comun.ip_local()}", font=("Arial", 12)).pack(pady=(12, 0))
    ttk.Label(f, text=f"Código: {cfg['codigo']}", font=("Arial", 12)).pack()
    estado = ttk.Label(f, text="Esperando al supervisor…", wraplength=320)
    estado.pack(pady=12)
    ttk.Label(f, text="Cerrar esta ventana detiene la supervisión.").pack()

    if not (licencia.marca_agua_removible() and cfg.get("ocultar_marca_agua")):
        marca_agua(root)

    def refrescar():
        if Servidor.error:
            estado.config(text=Servidor.error)
        elif Servidor.ultima:
            vivo = time.time() - Servidor.ultima < 5
            estado.config(text="Supervisor conectado" if vivo else "Esperando al supervisor…")
        root.after(1000, refrescar)
    refrescar()
    root.protocol("WM_DELETE_WINDOW", lambda: (srv.shutdown(), root.destroy()))
    root.mainloop()
