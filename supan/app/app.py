import sys

if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    if modo == "agente":
        import agente
        agente.main()
    elif modo == "supervisor":
        import supervisor
        supervisor.main()
    else:
        print("Uso: app.py agente|supervisor")
