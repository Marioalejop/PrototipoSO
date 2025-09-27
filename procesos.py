"""
Módulo: procesos.py
Responsabilidad: gestionar procesos y programación (scheduler) simple.
Componentes:
- class Proceso: representación de un proceso (PID, estado, instrucciones).
- class GestorProcesos: crea, elimina, y programa procesos (round-robin simple).

Se usa una cola de listos (ready). El scheduler ejecuta "quantum" instrucciones por proceso.
"""
import threading
import itertools
import time
from collections import deque
from typing import Callable, Deque, Dict, List, Optional

class Proceso:
    _pid_iter = itertools.count(1)

    def __init__(self, nombre: str, instrucciones: Optional[List[Callable]] = None, tiempo_total: float = 0.0):
        self.pid = next(Proceso._pid_iter)
        self.nombre = nombre
        self.instrucciones = instrucciones or []
        self.pc = 0  # contador de programa (índice de instrucción)
        self.estado = "ready"  # ready, running, waiting, terminated
        self.tiempo_total = tiempo_total  # tiempo consumido (simulación)
        self.metadata = {}

    def ejecutar_instruccion(self):
        """Ejecuta la instrucción actual si existe."""
        if self.pc >= len(self.instrucciones):
            return False
        instr = self.instrucciones[self.pc]
        try:
            instr(self)
        except Exception as e:
            # Manejo simple de excepción: marcar terminado
            print(f"[Proceso {self.pid}] Error en instrucción: {e}")
            self.estado = "terminated"
            return False
        self.pc += 1
        return True

    def is_finished(self) -> bool:
        return self.pc >= len(self.instrucciones) or self.estado == "terminated"


class GestorProcesos:
    """Gestor y scheduler simple con Round-Robin."""

    def __init__(self, quantum: int = 1):
        self.quantum = quantum
        self.ready_queue: Deque[Proceso] = deque()
        self.lock = threading.RLock()
        self._running = False
        self._scheduler_thread: Optional[threading.Thread] = None

    def crear_proceso(self, nombre: str, instrucciones: Optional[List[Callable]] = None) -> Proceso:
        with self.lock:
            p = Proceso(nombre, instrucciones)
            self.ready_queue.append(p)
            return p

    def listar_procesos(self) -> List[Dict]:
        with self.lock:
            return [{"pid": p.pid, "nombre": p.nombre, "estado": p.estado, "pc": p.pc} for p in list(self.ready_queue)]

    def terminar_proceso(self, pid: int) -> bool:
        with self.lock:
            for p in list(self.ready_queue):
                if p.pid == pid:
                    p.estado = "terminated"
                    try:
                        self.ready_queue.remove(p)
                    except ValueError:
                        pass
                    return True
        return False

    def _schedule_once(self):
        """Ejecuta un ciclo de scheduling: toma el primer proceso y le da `quantum` instrucciones."""
        with self.lock:
            if not self.ready_queue:
                return
            p = self.ready_queue.popleft()
            if p.estado == "terminated":
                return
            p.estado = "running"
        # Ejecutar fuera del lock para permitir que otros comandos interactúen
        for _ in range(self.quantum):
            if p.is_finished():
                break
            p.ejecutar_instruccion()
            # Simular que consume algo de tiempo
            p.tiempo_total += 0.01
        with self.lock:
            if p.is_finished():
                p.estado = "terminated"
                # no re-enqueue
            else:
                p.estado = "ready"
                self.ready_queue.append(p)

    def iniciar(self):
        if self._running:
            return
        self._running = True
        def loop():
            while self._running:
                self._schedule_once()
                time.sleep(0.01)  # pequeño retraso para evitar CPU spin
        self._scheduler_thread = threading.Thread(target=loop, daemon=True)
        self._scheduler_thread.start()

    def detener(self):
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=1)


# Instrucción de ejemplo (puede pasarse al crear procesos)

def instruccion_imprimir_factory(mensaje: str):
    def instr(proceso: Proceso):
        print(f"[Proceso {proceso.pid} - {proceso.nombre}] {mensaje}")
    return instr


if __name__ == "__main__":
    g = GestorProcesos(quantum=2)
    p1 = g.crear_proceso("p1", instrucciones=[instruccion_imprimir_factory("hola") for _ in range(4)])
    p2 = g.crear_proceso("p2", instrucciones=[instruccion_imprimir_factory("mundo") for _ in range(3)])
    g.iniciar()
    import time
    time.sleep(0.2)
    g.detener()
    print("Listado final:", g.listar_procesos())