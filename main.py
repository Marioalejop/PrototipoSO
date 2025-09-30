"""
Archivo: main.py
Punto de entrada del prototipo: inicializa memoria, gestor de procesos y shell.
Use el flag --gui para abrir la interfaz Tkinter.
"""
import sys
import procesos
import memoria
import shell

def main_cli():
    g = procesos.GestorProcesos(quantum=2)
    m = memoria.Memoria(frames=32, frame_size=256)
    g.iniciar()
    try:
        sh = shell.Shell(g, m)
        sh.start()
    finally:
        g.detener()

def main():
    if "--gui" in sys.argv:
        # Cargar la GUI
        from gui import main as gui_main
        gui_main()
    else:
        main_cli()

if __name__ == "__main__":
    main()
