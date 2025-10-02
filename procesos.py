"""
Módulo: procesos.py
Responsabilidad: gestionar procesos y programación (scheduler) simple.
Componentes:
- class Proceso: representación de un proceso (PID, estado, instrucciones).
- class GestorProcesos: crea, elimina, y programa procesos (round-robin simple).

Se usa una cola de listos (ready). El scheduler ejecuta "quantum" instrucciones por proceso.
Fixes: Crea 3 procesos demo en iniciar(), integra con Memoria, estados en español.
"""
import threading
import itertools
import time
from collections import deque
from typing import Callable, Deque, Dict, List, Optional

# Factory para instrucciones demo (tu original)
def instruccion_imprimir_factory(mensaje: str):
    def instr(proceso: Proceso):
        print(f"[Proceso {proceso.pid} - {proceso.nombre}] {mensaje}")
    return instr

class Proceso:
    _pid_iter = itertools.count(1)

    def __init__(self, nombre: str, instrucciones: Optional[List[Callable]] = None, tiempo_total: float = 0.0):
        self.pid = next(Proceso._pid_iter)
        self.nombre = nombre
        self.instrucciones = instrucciones or []
        self.pc = 0  # contador de programa
        self.estado = "listo"  # listo, ejecutando, bloqueado, terminado (español para GUI)
        self.tiempo_total = tiempo_total
        self.metadata = {}

    def ejecutar_instruccion(self):
        """Ejecuta la instrucción actual. Simula tiempo."""
        if self.pc >= len(self.instrucciones):
            return False
        instr = self.instrucciones[self.pc]
        try:
            instr(self)
        except Exception as e:
            print(f"[Proceso {self.pid}] Error: {e}")
            self.estado = "terminado"
            return False
        self.pc += 1
        time.sleep(0.5)  # Simula CPU time (visibilidad en logs/GUI)
        self.tiempo_total += 0.5
        return True

    def is_finished(self) -> bool:
        return self.pc >= len(self.instrucciones) or self.estado == "terminado"


class GestorProcesos:
    """Gestor y scheduler simple con Round-Robin."""

    def __init__(self, mem, quantum: int = 2):  # Recibe mem
        self.mem = mem
        self.quantum = quantum
        self.ready_queue: Deque[Proceso] = deque()
        self._all_procesos: Dict[int, Proceso] = {}  # Trackea todos
        self.lock = threading.RLock()
        self._running = False
        self._scheduler_thread: Optional[threading.Thread] = None

    def crear_proceso(self, nombre: str, instrucciones: Optional[List[Callable]] = None) -> Proceso:
        with self.lock:
            p = Proceso(nombre, instrucciones)
            self.ready_queue.append(p)
            self._all_procesos[p.pid] = p
            # Asigna memoria (4 frames)
            asignados = self.mem.allocate_frames(p.pid, 4)
            if asignados:
                p.metadata['frames'] = asignados  # Para uso futuro
                print(f"Proceso '{nombre}' (PID {p.pid}) creado con frames {asignados}")
            else:
                print(f"ERROR: No hay memoria para PID {p.pid}")
            return p

    def listar_procesos(self) -> List[Dict]:  # Retorna lista de dicts para shell/GUI
        with self.lock:
            return [{"pid": p.pid, "nombre": p.nombre, "estado": p.estado, "pc": p.pc} 
                    for p in self._all_procesos.values()]

    def terminar_proceso(self, pid: int) -> bool:
        with self.lock:
            if pid in self._all_procesos:
                p = self._all_procesos[pid]
                p.estado = "terminado"
                try:
                    self.ready_queue.remove(p)
                except ValueError:
                    pass
                self.mem.free_frames(pid)  # Libera memoria
                print(f"Proceso PID {pid} terminado y memoria liberada.")
                return True
        print(f"PID {pid} no encontrado.")
        return False

    def _schedule_once(self):
        with self.lock:
            if not self.ready_queue:
                return
            p = self.ready_queue.popleft()
            if p.estado == "terminado":
                return
            p.estado = "ejecutando"
        # Ejecuta quantum
        for _ in range(self.quantum):
            if p.is_finished():
                break
            p.ejecutar_instruccion()
        with self.lock:
            if p.is_finished():
                p.estado = "terminado"
            else:
                p.estado = "listo"
                self.ready_queue.append(p)
            print(f"[Scheduler] Proceso {p.pid} pausado (PC: {p.pc})")

    def iniciar(self):
        if self._running:
            return
        self._running = True
        # Crea 3 procesos demo automáticamente
        def instr_demo(proceso: Proceso):
            print(f"[Proceso {proceso.pid} - {proceso.nombre}] Ejecutando instrucción {proceso.pc + 1}/10")
        instr_list = [instruccion_imprimir_factory(f"Ejecutando...") for _ in range(10)]  # 10 instr cada uno
        for i, nombre in enumerate(["Proceso1", "Proceso2", "Proceso3"], 1):
            self.crear_proceso(nombre, instr_list)
        print("Gestor iniciado con 3 procesos demo. Alternancia comienza...")

        def loop():
            while self._running:
                self._schedule_once()
                time.sleep(0.1)  # Evita CPU alta
        self._scheduler_thread = threading.Thread(target=loop, daemon=True)
        self._scheduler_thread.start()

    def detener(self):
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=1)
            print("Scheduler detenido.")


if __name__ == "__main__":
    # Test (necesita mem para simular)
    from memoria import Memoria  # Importa tu memoria
    m = Memoria(frames=32)
    g = GestorProcesos(m, quantum=2)
    g.iniciar()  # Crea 3 demo
    time.sleep(3)  # Ve alternancia
    print(g.listar_procesos())  # Lista los 3
    g.detener()