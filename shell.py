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
        # Diccionario con descripciones de cada comando (incluyendo alias en español)
        self.descriptions = {
            # Base
            "help": "Muestra la lista de comandos disponibles y su descripción.",
            "ls": "Lista los archivos en el disco virtual.",
            "cat": "Muestra el contenido de un archivo. Uso: cat <archivo>",
            "write": "Crea o sobrescribe un archivo. Uso: write <archivo> <contenido>",
            "rm": "Elimina un archivo del disco virtual. Uso: rm <archivo>",
            "formatear": "Borra todos los archivos del disco virtual.",
            "run": "Crea y ejecuta un proceso de ejemplo. Uso: run <nombre_proceso>",
            "ps": "Muestra la lista de procesos en ejecución.",
            "kill": "Termina un proceso por su PID. Uso: kill <pid>",
            "memstat": "Muestra estadísticas de la memoria principal.",
            "exit": "Cierra el shell.",

            # Alias en español
            "ayuda": "Muestra la lista de comandos disponibles y su descripción.",
            "listar": "Lista los archivos en el disco virtual.",
            "lista": "Lista los archivos en el disco virtual.",
            "ver": "Muestra el contenido de un archivo. Uso: ver <archivo>",
            "mostrar": "Muestra el contenido de un archivo. Uso: mostrar <archivo>",
            "escribir": "Crea o sobrescribe un archivo. Uso: escribir <archivo> <contenido>",
            "borrar": "Elimina un archivo del disco virtual. Uso: borrar <archivo>",
            "eliminar": "Elimina un archivo del disco virtual. Uso: eliminar <archivo>",
            "ejecutar": "Crea y ejecuta un proceso de ejemplo. Uso: ejecutar <nombre_proceso>",
            "crearproceso": "Crea y ejecuta un proceso de ejemplo. Uso: crearproceso <nombre_proceso>",
            "procesos": "Muestra la lista de procesos en ejecución.",
            "terminar": "Termina un proceso por su PID. Uso: terminar <pid>",
            "memoria": "Muestra estadísticas de la memoria principal.",
            "salir": "Cierra el shell."
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
        for cmd in sorted(self.commands.keys()):
            desc = self.descriptions.get(cmd, "Sin descripción")
            print(f" - {cmd:10} {desc}")

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
        procesos_lista = self.gestor.listar_procesos()
        if not procesos_lista:
            print("No hay procesos en ejecución.")
            return
        for p in procesos_lista:
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
        stats = self.mem.status()
        print("=== Estado de la Memoria ===")
        print(f"Marcos totales : {stats['frames_total']}")
        print(f"Marcos usados  : {stats['frames_used']}")
        print(f"Marcos libres  : {stats['frames_free']}")
        print(f"Tamaño de marco: {stats['frame_size']} bytes")
        # Mapear PID -> nombre (si el gestor lo provee)
        pid_map = {}
        try:
            for p in self.gestor.listar_procesos():
                pid_map[p['pid']] = p.get('nombre', '?')
        except Exception:
            pass
        print("\nMarcos:")
        owners = getattr(self.mem, "_owner", {})
        for i in range(stats['frames_total']):
            owner = owners.get(i)
            if owner is None:
                print(f" {i:3}: libre")
            else:
                name = pid_map.get(owner, "?")
                print(f" {i:3}: PID={owner} / {name}")

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