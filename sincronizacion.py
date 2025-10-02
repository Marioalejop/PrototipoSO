"""
Módulo: sincronizacion.py
Contiene:
- Clase Semaforo
- Clase Mutex (basado en threading.Lock)

Estas primitivas usan las implementaciones de `threading` de Python pero ofrecen una API simple.
"""
import threading
import time

class Mutex:
    def __init__(self):
        self._lock = threading.Lock()

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        if timeout is None or timeout < 0:
            return self._lock.acquire(blocking)
        else:
            return self._lock.acquire(blocking, timeout)

    def release(self):
        self._lock.release()


class Semaforo:
    def __init__(self, value: int = 1):
        self._sem = threading.Semaphore(value)

    def down(self, timeout: float = None) -> bool:
        """Baja (P). Si timeout es None espera indefinidamente."""
        if timeout is None:
            self._sem.acquire()
            return True
        else:
            return self._sem.acquire(timeout=timeout)

    def up(self):
        """Sube (V)."""
        self._sem.release()


if __name__ == "__main__":
    s = Semaforo(2)
    print(s.down(0.01))
    s.up()