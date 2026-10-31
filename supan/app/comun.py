import json, secrets, socket
from pathlib import Path

PUERTO = 8765
DIR = Path.home() / ".supervisor_pantalla"
ARCHIVO = DIR / "config.json"


def cargar():
    try:
        return json.loads(ARCHIVO.read_text("utf-8"))
    except (OSError, ValueError):
        return {}


def guardar(cfg):
    DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVO.write_text(json.dumps(cfg, indent=2), "utf-8")
    try:
        ARCHIVO.chmod(0o600)
    except OSError:
        pass


def nuevo_codigo():
    return "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(8))


def ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()
