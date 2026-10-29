# SuPan
### (Screen Supervisor / Supervisor de pantalla) 

Version / Versión: "1.0.0"
Status / Estado: Initial release / Versión inicial
Platforms / Plataformas: Windows and Linux / Windows y Linux

«English: A desktop screen-supervision tool for families and educators. It provides a supervisor interface, a visible notice on the monitored computer, connection by IP address and access code, and a graphical installer that handles dependencies and reports errors.

Español: Herramienta de escritorio para supervisar pantallas, pensada para familias y docentes. Incluye una interfaz de supervisión, un aviso visible en el equipo supervisado, conexión mediante dirección IP y código de acceso, y un instalador gráfico que gestiona dependencias e informa de errores.»

---

English

Features

- Supervisor mode: Enter a device name, IP address, and access code, then view the remote screen.
- Monitored-device mode: Displays a persistent notice that the screen is being supervised, along with the IP address and a code needed to connect.
- Graphical installer: Creates a Python virtual environment, installs required dependencies, offers shortcuts, and writes an installation log when errors occur.
- Future licensing groundwork: "app/licencia.py" provides a starting point for a future license system. Version 1.0.0 does not show payment options or paid features.

Requirements

- Python 3.9 or newer.

- Windows or Linux with a graphical desktop session.

- On Linux, Tkinter and Python virtual-environment support. On Debian/Ubuntu, install them with:
  
  sudo apt install python3-tk python3-venv

- Both computers must be reachable on the same local network. Allow TCP port "8765" on the monitored computer through the local firewall as needed.

Installation

Windows

1. Install Python 3.9 or newer if it is not already installed.
2. Extract the entire project folder.
3. Run "instalar.bat".
4. Choose the desired mode in the installer and select Install.

Linux

1. Install Python, Tkinter, and "venv" using your distribution's package manager.
2. Extract the entire project folder.
3. Run "./instalar.sh" in a terminal. If necessary, make it executable with "chmod +x instalar.sh".
4. Choose the desired mode in the installer.

The installer creates a virtual environment and attempts to install dependencies automatically. If installation fails, read the displayed error and check "supervisor_instalacion.log" in the system temporary directory.

First use

1. Install and open Monitored Screen on the computer to be supervised.
2. Note the IP address and access code shown in its window.
3. Install and open Screen Supervisor on the other computer.
4. Enter the IP address and code, provide a device name, and select Connect.
5. Select Disconnect in the supervisor or close the monitored application to end the session.

Privacy and security

- Use this software only with appropriate authorization, and clearly inform the person using the monitored computer when their screen is being shared.
- The monitored application displays a visible notice. Closing it stops its service.
- Version 1.0.0 sends screenshots over unencrypted HTTP. The access code is a basic access control, not encryption or a complete security guarantee. Use only on a trusted local network. Do not expose port "8765" to the Internet or use the application on public networks. Before real-world deployment, add HTTPS/transport security and review firewall rules.
- Screen-capture compatibility depends on the operating system and desktop session. Capture may not work in some Wayland sessions.

Not included in version 1.0.0

- Removing the watermark through a license.
- Supervising multiple computers simultaneously.
- Purchase, subscription, or payment-activation interfaces.

These features are intentionally not displayed or enabled in this release. "app/licencia.py" is only a starting point for future licensing work.

Project structure

supervisor_pantalla/
├── app/
│   ├── agente.py       # Monitored-device service and visible notice
│   ├── app.py          # Entry point for both modes
│   ├── comun.py        # Shared configuration and network utilities
│   ├── licencia.py     # Extension point for future licensing
│   └── supervisor.py   # Supervisor interface
├── instalador.py       # Graphical installer and error handling
├── instalar.bat        # Windows launcher
├── instalar.sh         # Linux launcher
├── README.md
├── VERSION
└── CHANGELOG.md

---

Español

Características

- Modo supervisor: permite introducir el nombre del equipo, su dirección IP y el código de acceso para visualizar la pantalla remota.
- Modo equipo supervisado: muestra un aviso persistente de que la pantalla está siendo supervisada, junto con la dirección IP y el código necesario para conectarse.
- Instalador gráfico: crea un entorno virtual de Python, instala las dependencias necesarias, ofrece accesos directos y guarda un registro si ocurre un error.
- Base para licencias futuras: "app/licencia.py" sirve como punto de partida para un sistema de licencias. La versión 1.0.0 no muestra opciones de pago ni funciones de pago.

Requisitos

- Python 3.9 o posterior.

- Windows o Linux con un entorno de escritorio gráfico.

- En Linux, Tkinter y soporte para entornos virtuales de Python. En Debian/Ubuntu, instala ambos con:
  
  sudo apt install python3-tk python3-venv

- Ambos equipos deben poder comunicarse por la misma red local. Si hace falta, permite el puerto TCP "8765" en el firewall del equipo supervisado.

Instalación

Windows

1. Instala Python 3.9 o posterior si todavía no está instalado.
2. Extrae la carpeta completa del proyecto.
3. Ejecuta "instalar.bat".
4. Selecciona el modo deseado en el instalador y pulsa Instalar.

Linux

1. Instala Python, Tkinter y "venv" mediante el gestor de paquetes de tu distribución.
2. Extrae la carpeta completa del proyecto.
3. Ejecuta "./instalar.sh" desde una terminal. Si es necesario, dale permiso de ejecución con "chmod +x instalar.sh".
4. Selecciona el modo deseado en el instalador.

El instalador crea un entorno virtual e intenta instalar las dependencias automáticamente. Si falla, revisa el error mostrado y el archivo "supervisor_instalacion.log" en la carpeta temporal del sistema.

Primer uso

1. Instala y abre Pantalla supervisada en el equipo que se va a supervisar.
2. Anota la dirección IP y el código que aparecen en su ventana.
3. Instala y abre Supervisor de pantalla en el otro equipo.
4. Introduce la IP y el código, escribe un nombre para el equipo y pulsa Conectar.
5. Para terminar la sesión, pulsa Desconectar en el supervisor o cierra la aplicación del equipo supervisado.

Privacidad y seguridad

- Utiliza este programa únicamente con la autorización correspondiente e informa claramente a la persona que usa el equipo cuando su pantalla se esté compartiendo.
- La aplicación del equipo supervisado muestra un aviso visible. Al cerrarla, se detiene el servicio.
- La versión 1.0.0 transmite capturas mediante HTTP sin cifrado. El código de acceso es un control básico, no es cifrado ni una garantía completa de seguridad. Úsala únicamente en una red local de confianza. No expongas el puerto "8765" a Internet ni la utilices en redes públicas. Antes de un despliegue real, añade HTTPS/seguridad de transporte y revisa las reglas del firewall.
- La compatibilidad de captura depende del sistema operativo y del entorno gráfico. Puede no funcionar en algunas sesiones Wayland.

No incluido en la versión 1.0.0

- Quitar la marca de agua mediante una licencia.
- Supervisar varios computadores simultáneamente.
- Interfaces de compra, suscripción o activación de pagos.

Estas funciones no se muestran ni están habilitadas en esta versión. "app/licencia.py" es únicamente una base para desarrollar el sistema de licencias en el futuro.

Estructura del proyecto

supervisor_pantalla/
├── app/
│   ├── agente.py       # Servicio del equipo supervisado y aviso visible
│   ├── app.py          # Punto de entrada para ambos modos
│   ├── comun.py        # Configuración compartida y utilidades de red
│   ├── licencia.py     # Punto de extensión para licencias futuras
│   └── supervisor.py   # Interfaz del supervisor
├── instalador.py       # Instalador gráfico y manejo de errores
├── instalar.bat        # Lanzador para Windows
├── instalar.sh        # Lanzador para Linux
├── README.md
├── VERSION
└── CHANGELOG.md