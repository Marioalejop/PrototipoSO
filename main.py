"""
Archivo: main.py
Punto de entrada del prototipo: inicializa memoria, gestor de procesos y shell.
"""
import procesos
import memoria
import shell


def main():
    g = procesos.GestorProcesos(quantum=2)
    m = memoria.Memoria(frames=32, frame_size=256)
    g.iniciar()
    try:
        sh = shell.Shell(g, m)
        sh.start()
    finally:
        g.detener()


if __name__ == "__main__":
    main()