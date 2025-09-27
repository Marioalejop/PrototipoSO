"""
Módulo: memoria.py
Responsabilidad: simular una memoria principal simple con marcos (frames)
Proporciona:
- Clase Memoria: gestionar lectura/escritura, asignación de bloques.
- Manejo básico de direcciones virtuales (simple offset)

Diseño educativo: no pretende ser una implementación completa de paginación.
"""
from typing import Dict, Optional
import threading

class Memoria:
    """Simula memoria física dividida en marcos de tamaño fijo."""

    def __init__(self, frames: int = 32, frame_size: int = 256):
        self.frames = frames
        self.frame_size = frame_size
        # Memoria real representada como diccionario: frame_index -> bytes
        self._mem: Dict[int, bytearray] = {i: bytearray(frame_size) for i in range(frames)}
        # Tabla de ocupación simple: frame_index -> pid (None si libre)
        self._owner: Dict[int, Optional[int]] = {i: None for i in range(frames)}
        self._lock = threading.RLock()

    def status(self) -> Dict[str, int]:
        """Devuelve estadísticas básicas de la memoria."""
        with self._lock:
            used = sum(1 for v in self._owner.values() if v is not None)
            free = self.frames - used
            return {"frames_total": self.frames, "frames_used": used, "frames_free": free, "frame_size": self.frame_size}

    def allocate_frames(self, pid: int, count: int) -> Optional[list]:
        """Asigna `count` marcos al proceso pid. Devuelve la lista de índices o None si no hay suficiente espacio."""
        with self._lock:
            free_frames = [i for i, owner in self._owner.items() if owner is None]
            if len(free_frames) < count:
                return None
            allocated = free_frames[:count]
            for i in allocated:
                self._owner[i] = pid
                # Limpia el contenido
                self._mem[i] = bytearray(self.frame_size)
            return allocated

    def free_frames(self, pid: int) -> None:
        """Libera todos los marcos pertenecientes al pid."""
        with self._lock:
            for i, owner in list(self._owner.items()):
                if owner == pid:
                    self._owner[i] = None
                    self._mem[i] = bytearray(self.frame_size)

    def write(self, frame_index: int, offset: int, data: bytes) -> bool:
        """Escribe `data` en el frame y offset dado. Devuelve False si se sale de límites."""
        with self._lock:
            if frame_index not in self._mem:
                return False
            if offset < 0 or offset + len(data) > self.frame_size:
                return False
            self._mem[frame_index][offset:offset+len(data)] = data
            return True

    def read(self, frame_index: int, offset: int, size: int) -> Optional[bytes]:
        with self._lock:
            if frame_index not in self._mem:
                return None
            if offset < 0 or offset + size > self.frame_size:
                return None
            return bytes(self._mem[frame_index][offset:offset+size])


if __name__ == "__main__":
    m = Memoria(frames=8, frame_size=64)
    print(m.status())
    print("Asignando 3 marcos a pid=1 ->", m.allocate_frames(1, 3))
    print(m.status())
    m.free_frames(1)
    print(m.status())