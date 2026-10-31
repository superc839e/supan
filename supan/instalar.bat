@echo off
where pyw >nul 2>nul && (start "" pyw -3 "%~dp0instalador.py" & exit /b)
where pythonw >nul 2>nul && (start "" pythonw "%~dp0instalador.py" & exit /b)
echo No se encontro Python. Se abrira la pagina de descarga.
echo Instala Python 3.9 o superior (marca "Add python.exe to PATH") y ejecuta este archivo otra vez.
start https://www.python.org/downloads/windows/
pause
