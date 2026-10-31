"""Equipo del PADRE/PROFESOR: muestra la pantalla del equipo supervisado."""
import io, re, threading, time
import tkinter as tk
import urllib.error, urllib.request
from tkinter import messagebox, ttk

from PIL import Image, ImageOps, ImageTk

import comun, licencia


class App:
    def __init__(self):
        self.cfg = comun.cargar()
        eq = ((self.cfg.get("equipos") or [{}])[:licencia.max_equipos()])[0]
        self.gen, self.frame, self.msg, self.fatal, self.conectado = 0, None, "Sin conexión", None, False
        r = self.r = tk.Tk()
        r.title("Supervisor de pantalla")
        r.geometry("960x640")
        barra = ttk.Frame(r, padding=8)
        barra.pack(fill="x")
        self.v = {k: tk.StringVar(value=eq.get(k, "")) for k in ("nombre", "ip", "codigo")}
        for etiqueta, k, ancho in (("Nombre", "nombre", 14), ("Dirección", "ip", 18), ("Código", "codigo", 10)):
            ttk.Label(barra, text=etiqueta).pack(side="left", padx=(8, 2))
            ttk.Entry(barra, textvariable=self.v[k], width=ancho).pack(side="left")
        self.boton = ttk.Button(barra, text="Conectar", command=self.alternar)
        self.boton.pack(side="left", padx=12)
        self.lienzo = tk.Canvas(r, bg="black", highlightthickness=0)
        self.lienzo.pack(fill="both", expand=True)
        self.estado = ttk.Label(r, padding=4, anchor="w")
        self.estado.pack(fill="x")
        self.tick()

    def alternar(self):
        if self.conectado:
            return self.desconectar()
        ip, cod = self.v["ip"].get().strip(), self.v["codigo"].get().strip().upper()
        if not re.fullmatch(r"[\w.\-]+", ip) or len(cod) < 4:
            return messagebox.showwarning("Datos incompletos",
                                          "Escribe la dirección y el código que muestra el equipo supervisado.")
        self.cfg["equipos"] = [{"nombre": self.v["nombre"].get().strip(), "ip": ip, "codigo": cod}]
        comun.guardar(self.cfg)
        self.gen += 1
        self.conectado = True
        self.boton.config(text="Desconectar")
        self.msg = "Conectando…"
        threading.Thread(target=self.bucle, args=(self.gen, ip, cod), daemon=True).start()

    def desconectar(self, msg="Sin conexión"):
        self.gen += 1
        self.conectado = False
        self.boton.config(text="Conectar")
        self.msg = msg
        self.lienzo.delete("all")

    def bucle(self, g, ip, cod):
        url = f"http://{ip}:{comun.PUERTO}/frame"
        while g == self.gen:
            t0 = time.time()
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"X-Codigo": cod}), timeout=5) as r:
                    datos = r.read()
                if g == self.gen:
                    self.frame, self.msg = (g, datos), "Conectado"
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    self.fatal = "Código incorrecto."
                    return
                self.msg = f"El equipo respondió con error {e.code} (¿captura no permitida?). Reintentando…"
            except (urllib.error.URLError, OSError):
                self.msg = "No se encuentra el equipo. Revisa la dirección, que estén en la misma red y el firewall. Reintentando…"
            except Exception as e:
                self.msg = f"Error: {e}. Reintentando…"
            time.sleep(max(0.0, 0.5 - (time.time() - t0)))

    def tick(self):
        if self.fatal:
            m, self.fatal = self.fatal, None
            self.desconectar(m)
            messagebox.showwarning("No se pudo conectar", m)
        f, self.frame = self.frame, None
        if f and f[0] == self.gen:
            w, h = self.lienzo.winfo_width(), self.lienzo.winfo_height()
            if w > 1 and h > 1:
                self.foto = ImageTk.PhotoImage(ImageOps.contain(Image.open(io.BytesIO(f[1])), (w, h)))
                self.lienzo.delete("all")
                self.lienzo.create_image(w // 2, h // 2, image=self.foto)
        self.estado.config(text=self.msg)
        self.r.after(100, self.tick)


def main():
    App().r.mainloop()
