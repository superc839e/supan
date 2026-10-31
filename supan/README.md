# Supervisor de pantalla

Mira la pantalla del computador de tu hijo o estudiante desde otro equipo de la misma red.
El equipo supervisado muestra siempre un aviso rojo: **● Pantalla supervisada**.

## Instalar

1. Descomprime TODA la carpeta.
2. Windows: doble clic en `instalar.bat`. Linux: `./instalar.sh`.
3. Elige qué equipo es:
   - **Supervisor**: el del padre o profesor (ve las pantallas).
   - **Supervisado**: el del hijo o estudiante.

Requisitos: Python 3.9 o superior. Si no lo tienes, el instalador de Windows abre la página de descarga.
En Linux también necesitas Tk (`python3-tk` en Debian/Ubuntu, `tk` en Arch/CachyOS).
No pide permisos de administrador.

## Usar

1. En el equipo supervisado, abre **Pantalla supervisada**. Verás su dirección y un código.
2. En tu equipo, abre **Supervisor de pantalla**, escribe la dirección y el código, y pulsa **Conectar**.
3. Los datos se guardan para la próxima vez.

Cerrar la ventana del equipo supervisado detiene la supervisión.

## Problemas comunes

| Problema | Solución |
|---|---|
| "No se encuentra el equipo" | Revisa la dirección, que ambos estén en la misma red y el firewall. |
| "Código incorrecto" | Copia el código tal como aparece en el equipo supervisado. |
| Windows pregunta por el firewall | Elige **Permitir** en el equipo supervisado. |
| Pantalla negra o error de captura en Linux | Wayland no es compatible: inicia sesión en X11. |

## Desinstalar

Windows: Configuración → Aplicaciones → Supervisor de pantalla.
Linux: `python3 ~/.local/share/SupervisorPantalla/instalador.py --desinstalar`

## Límites

- Solo funciona en red local; el tráfico no está cifrado.
- Usa esta app solo con el conocimiento de quien es supervisado (hijos, estudiantes).

## Archivos

- `instalador.py`, `instalar.bat`, `instalar.sh`: instalador.
- `app/agente.py`: equipo supervisado.
- `app/supervisor.py`: equipo del supervisor.
- `app/licencia.py`: base para funciones de pago futuras.
