#!/usr/bin/env python3
"""Instalador de Supervisor de pantalla (Windows y Linux, sin permisos de administrador)."""
import json, os, queue, shutil, subprocess, sys, tempfile, threading, time, traceback
from pathlib import Path

APP, WIN = "SupervisorPantalla", os.name == "nt"
QUIEN = Path(__file__).resolve().parent
LOG = Path(tempfile.gettempdir()) / "supervisor_instalacion.log"
SIN_VENTANA = 0x08000000 if WIN else 0  # CREATE_NO_WINDOW
NOMBRES = {"supervisor": "Supervisor de pantalla", "agente": "Pantalla supervisada"}
UNINSTALL_KEY = rf"Software\Microsoft\Windows\CurrentVersion\Uninstall\{APP}"
SALIDA = print


class Fallo(Exception):
    """Error con un mensaje listo para mostrar al usuario."""


def log(msg):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")
    SALIDA(msg)


def ejecutar(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, creationflags=SIN_VENTANA, **kw)
    if r.returncode:
        log((r.stdout + r.stderr)[-1500:])
    return r


def destino_defecto():
    base = Path(os.environ.get("LOCALAPPDATA", Path.home())) if WIN else Path.home() / ".local/share"
    return base / APP


def crear_atajo(destino, rol, py, donde):
    nombre, app = NOMBRES[rol], destino / "app" / "app.py"
    if WIN:
        base = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs"
        ruta = base / ("Startup" if donde == "inicio" else "") / f"{nombre}.lnk"
        ps = ("$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{}');$s.TargetPath='{}';"
              "$s.Arguments='\"{}\" {}';$s.WorkingDirectory='{}';$s.Save()").format(
            *(str(x).replace("'", "''") for x in (ruta, py, app, rol, destino)))
        if ejecutar(["powershell", "-NoProfile", "-Command", ps]).returncode:
            log(f"No se pudo crear el acceso directo ({donde}).")
            return []
    else:
        base = Path.home() / (".config/autostart" if donde == "inicio" else ".local/share/applications")
        base.mkdir(parents=True, exist_ok=True)
        ruta = base / f"{APP}-{rol}.desktop"
        ruta.write_text(f'[Desktop Entry]\nType=Application\nName={nombre}\n'
                        f'Exec="{py}" "{app}" {rol}\nTerminal=false\nCategories=Utility;\n', encoding="utf-8")
    return [str(ruta)]


def abrir_firewall():
    from app.comun import PUERTO
    r = ejecutar(["netsh", "advfirewall", "firewall", "add", "rule", f"name={APP}", "dir=in",
                  "action=allow", "protocol=TCP", f"localport={PUERTO}"])
    if r.returncode:
        log("No se pudo abrir el firewall (requiere administrador). Si Windows pregunta al abrir la app, elige «Permitir».")
    return r.returncode == 0


def registrar_desinstalador(destino):
    import winreg
    datos = {"DisplayName": "Supervisor de pantalla", "DisplayVersion": "1.0", "InstallLocation": str(destino),
             "UninstallString": f'"{sys.executable}" "{destino / "instalador.py"}" --desinstalar'}
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY) as k:
        for n, v in datos.items():
            winreg.SetValueEx(k, n, 0, winreg.REG_SZ, v)


def instalar(rol, destino, atajo, inicio):
    """Devuelve el comando para abrir la app. Si algo falla, deshace lo que creó."""
    destino = Path(destino).expanduser().resolve()
    if sys.version_info < (3, 9):
        raise Fallo("Se necesita Python 3.9 o superior.")
    if not (QUIEN / "app" / "app.py").exists():
        raise Fallo("Faltan archivos de la aplicación. Descomprime TODA la carpeta antes de instalar.")
    existente = next((p for p in (destino, *destino.parents) if p.exists()), Path.home())
    if shutil.disk_usage(existente).free < 200 * 2**20:  # en la unidad donde se instalará
        raise Fallo("Poco espacio en disco (se necesitan unos 200 MB).")
    if destino.exists() and any(destino.iterdir()) and not (destino / "instalacion.json").exists():
        raise Fallo(f"La carpeta {destino} ya existe y no está vacía. Elige otra carpeta.")
    if rol == "agente" and not WIN and os.environ.get("XDG_SESSION_TYPE") == "wayland":
        log("Aviso: en Wayland la captura de pantalla puede fallar. Si pasa, inicia sesión en X11.")

    creado, rutas = not destino.exists(), []
    try:
        log("Copiando archivos…")
        try:
            destino.mkdir(parents=True, exist_ok=True)
            shutil.copytree(QUIEN / "app", destino / "app", dirs_exist_ok=True)
            shutil.copy2(QUIEN / "instalador.py", destino / "instalador.py")
        except PermissionError:
            raise Fallo(f"No hay permiso para escribir en {destino}. Elige otra carpeta.")
        venv = destino / "venv"
        py = venv / ("Scripts/python.exe" if WIN else "bin/python")
        pyw = venv / ("Scripts/pythonw.exe" if WIN else "bin/python")
        if not py.exists():
            log("Creando entorno de Python…")
            if ejecutar([sys.executable, "-m", "venv", str(venv)]).returncode:
                raise Fallo("No se pudo crear el entorno de Python. En Debian/Ubuntu: sudo apt install python3-venv python3-tk")
        log("Instalando dependencias (puede tardar un minuto)…")
        paquetes = ["Pillow"] + (["mss"] if rol == "agente" else [])
        for intento in (1, 2, 3):
            if ejecutar([str(py), "-m", "pip", "install", "--disable-pip-version-check", *paquetes],
                        timeout=900).returncode == 0:
                break
            log(f"Intento {intento} de 3 falló.")
            time.sleep(3)
        else:
            raise Fallo("No se pudieron descargar las dependencias. Revisa tu conexión a Internet e inténtalo de nuevo.")
        if ejecutar([str(py), "-c", "import tkinter, PIL.ImageTk" + (", mss" if rol == "agente" else "")]).returncode:
            raise Fallo("Falta Tk o Pillow. En Linux instala Tk (Debian/Ubuntu: python3-tk · Arch/CachyOS: tk).")
        if atajo:
            rutas += crear_atajo(destino, rol, pyw, "menu")
        if inicio:
            rutas += crear_atajo(destino, rol, pyw, "inicio")
        firewall = False
        if WIN:
            firewall = rol == "agente" and abrir_firewall()
            registrar_desinstalador(destino)
        (destino / "instalacion.json").write_text(json.dumps({"rutas": rutas, "firewall": firewall}), "utf-8")
    except BaseException:
        for r in rutas:
            Path(r).unlink(missing_ok=True)
        if creado:
            shutil.rmtree(destino, ignore_errors=True)
        raise
    log("Instalación completada.")
    return [str(pyw), str(destino / "app" / "app.py"), rol]


def desinstalar(destino):
    m = destino / "instalacion.json"
    if not m.exists():
        raise Fallo(f"No se encontró una instalación en {destino}")
    datos = json.loads(m.read_text("utf-8"))
    for r in datos["rutas"]:
        Path(r).unlink(missing_ok=True)
    if WIN:
        import winreg
        if datos.get("firewall"):
            ejecutar(["netsh", "advfirewall", "firewall", "delete", "rule", f"name={APP}"])
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY)
        except OSError:
            pass
    try:
        shutil.rmtree(destino)
    except OSError as e:
        raise Fallo(f"No se pudo borrar {destino}. Cierra la aplicación y vuelve a intentarlo.\n{e}")


def gui():
    global SALIDA
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    r = tk.Tk()
    r.title("Instalador · Supervisor de pantalla")
    r.resizable(False, False)
    rol, ruta = tk.StringVar(value="supervisor"), tk.StringVar(value=str(destino_defecto()))
    atajo, inicio = tk.BooleanVar(value=True), tk.BooleanVar(value=False)
    cola = queue.Queue()
    SALIDA = lambda m: cola.put(("log", m))

    f = ttk.Frame(r, padding=16)
    f.pack()
    ttk.Label(f, text="¿Qué equipo es este?", font=("Arial", 12, "bold")).grid(sticky="w")
    ttk.Radiobutton(f, text="Equipo del padre o profesor (ve las pantallas)", value="supervisor", variable=rol).grid(sticky="w")
    ttk.Radiobutton(f, text="Equipo del hijo o estudiante (muestra un aviso permanente de supervisión)",
                    value="agente", variable=rol).grid(sticky="w")
    ttk.Label(f, text="Carpeta de instalación:").grid(sticky="w", pady=(12, 0))
    fila = ttk.Frame(f)
    fila.grid(sticky="ew")
    ttk.Entry(fila, textvariable=ruta, width=52).pack(side="left")

    def examinar():
        d = filedialog.askdirectory()
        if d:
            ruta.set(str(Path(d) / APP))
    ttk.Button(fila, text="Examinar…", command=examinar).pack(side="left", padx=4)
    ttk.Checkbutton(f, text="Crear acceso directo en el menú", variable=atajo).grid(sticky="w", pady=(8, 0))
    ttk.Checkbutton(f, text="Abrir al iniciar sesión", variable=inicio).grid(sticky="w")
    barra = ttk.Progressbar(f, mode="indeterminate")
    barra.grid(sticky="ew", pady=8)
    texto = tk.Text(f, height=8, width=66, state="disabled")
    texto.grid()
    boton = ttk.Button(f, text="Instalar")
    boton.grid(sticky="e", pady=(8, 0))

    def trabajo():
        try:
            cola.put(("ok", instalar(rol.get(), ruta.get(), atajo.get(), inicio.get())))
        except Fallo as e:
            cola.put(("error", str(e)))
        except Exception as e:
            log(traceback.format_exc())
            cola.put(("error", f"Error inesperado: {e}\n\nDetalles en: {LOG}"))

    def empezar():
        boton.state(["disabled"])
        barra.start(12)
        threading.Thread(target=trabajo, daemon=True).start()
    boton.config(command=empezar)

    def revisar():
        try:
            while True:
                tipo, dato = cola.get_nowait()
                if tipo == "log":
                    texto.config(state="normal")
                    texto.insert("end", dato + "\n")
                    texto.see("end")
                    texto.config(state="disabled")
                    continue
                barra.stop()
                boton.state(["!disabled"])
                if tipo == "error":
                    messagebox.showerror("No se pudo instalar", dato)
                elif messagebox.askyesno("Listo", "Instalación completada.\n¿Abrir la aplicación ahora?"):
                    subprocess.Popen(dato)
                    r.destroy()
                    return
                elif tipo == "ok":
                    r.destroy()
                    return
        except queue.Empty:
            pass
        r.after(100, revisar)
    revisar()
    r.mainloop()


def main():
    if "--desinstalar" in sys.argv:
        import tkinter as tk
        from tkinter import messagebox
        tk.Tk().withdraw()
        i = sys.argv.index("--desinstalar")
        d = Path(sys.argv[i + 1]) if len(sys.argv) > i + 1 else QUIEN
        try:
            if messagebox.askyesno("Desinstalar", f"¿Quitar Supervisor de pantalla de\n{d}?"):
                desinstalar(d)
                messagebox.showinfo("Listo", "Desinstalado.")
        except Fallo as e:
            messagebox.showerror("Desinstalar", str(e))
        return
    try:
        import tkinter  # noqa: F401
    except ImportError:
        sys.exit("Falta Tk. Debian/Ubuntu: sudo apt install python3-tk · Arch/CachyOS: sudo pacman -S tk")
    gui()


if __name__ == "__main__":
    main()
