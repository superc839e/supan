"""Base de las funciones de pago (próxima versión).
En esta versión todo está desactivado y ninguna pantalla lo menciona.
v2: validar aquí la clave de licencia y devolver True en activa()."""


def activa():
    return False


def marca_agua_removible():
    return activa()


def max_equipos():
    return 5 if activa() else 1
