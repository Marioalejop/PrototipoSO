"""
Módulo: shell.py
Responsabilidad: proporcionar una interfaz de línea de comandos simple para interactuar con el prototipo.
Comandos soportados:
- help
- ls
- cat <archivo>
- write <archivo> <contenido>
- rm <archivo>
- formatear
- run <nombre_proceso>
- ps
- kill <pid>
- memstat
- exit

El shell usa los módulos archivos, procesos y memoria.
"""
import shlex
from typing import List
import archivos
import procesos
import memoria


class Shell:
    def __init__(self, gestor: procesos.GestorProcesos, mem: memoria.Memoria):
        self.gestor = gestor
        self.mem = mem
        self.prompt = "prototipoOS> "
        # comandos mapeados a métodos
        self.commands = {
            "help": self.cmd_help,
            "ls": self.cmd_ls,
            "cat": self.cmd_cat,
            "write": self.cmd_write,
            "rm": self.cmd_rm,
            "formatear": self.cmd_formatear,
            "run": self.cmd_run,
            "ps": self.cmd_ps,
            "kill": self.cmd_kill,
            "memstat": self.cmd_memstat,
            "exit": self.cmd_exit,
        }
        self._running = False

    def start(self):
        self._running = True
        print("Bienvenido al prototipo de Shell. Escriba 'help' para ver comandos.")
        while self._running:
            try:
                linea = input(self.prompt)
            except EOFError:
                break
            linea = linea.strip()
            if not linea:
                continue
            parts = shlex.split(linea)
            cmd = parts[0]
            args = parts[1:]
            func = self.commands.get(cmd)
            if func:
                try:
                    func(args)
                except Exception as e:
                    print(f"Error ejecutando comando {cmd}: {e}")
            else:
                print(f"Comando no encontrado: {cmd}. Use 'help'.")

    # Comandos
    def cmd_help(self, args: List[str]):
        print("Comandos disponibles:")
        for k in sorted(self.commands.keys()):
            print(f" - {k}")

    def cmd_ls(self, args: List[str]):
        archivos_lista = archivos.listar_archivos()
        for a in archivos_lista:
            print(a)

    def cmd_cat(self, args: List[str]):
        if not args:
            print("Uso: cat <archivo>")
            return
        contenido = archivos.leer_archivo(args[0])
        if contenido is None:
            print("Archivo no encontrado")
        else:
            print(contenido)

    def cmd_write(self, args: List[str]):
        if len(args) < 2:
            print("Uso: write <archivo> <contenido>")
            return
        nombre = args[0]
        contenido = " ".join(args[1:])
        archivos.escribir_archivo(nombre, contenido)
        print("Escrito.")

    def cmd_rm(self, args: List[str]):
        if not args:
            print("Uso: rm <archivo>")
            return
        ok = archivos.borrar_archivo(args[0])
        print("Borrado." if ok else "No existe el archivo.")

    def cmd_formatear(self, args: List[str]):
        archivos.formatear_disco()
        print("Disco formateado.")

    def cmd_run(self, args: List[str]):
        if not args:
            print("Uso: run <nombre_proceso>")
            return
        nombre = args[0]
        # Por defecto crearemos un proceso que imprime su nombre 3 veces
        instr = [procesos.instruccion_imprimir_factory(f"ejecutando {nombre} {i}") for i in range(3)]
        p = self.gestor.crear_proceso(nombre, instrucciones=instr)
        print(f"Proceso creado con PID {p.pid}")

    def cmd_ps(self, args: List[str]):
        for p in self.gestor.listar_procesos():
            print(f"PID {p['pid']} - {p['nombre']} - {p['estado']} - PC={p['pc']}")

    def cmd_kill(self, args: List[str]):
        if not args:
            print("Uso: kill <pid>")
            return
        try:
            pid = int(args[0])
        except ValueError:
            print("PID inválido")
            return
        ok = self.gestor.terminar_proceso(pid)
        print("Terminó proceso." if ok else "No se encontró PID.")

    def cmd_memstat(self, args: List[str]):
        print(self.mem.status())

    def cmd_exit(self, args: List[str]):
        print("Saliendo del shell...")
        self._running = False


if __name__ == "__main__":
    g = procesos.GestorProcesos(quantum=1)
    m = memoria.Memoria(frames=16, frame_size=128)
    g.iniciar()
    try:
        Shell(g, m).start()
    finally:
        g.detener()