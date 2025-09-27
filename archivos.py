"""
Módulo: archivos.py
Responsabilidad: manejar un disco virtual simple contenido en `disco_virtual.txt`.
Formato simple: cada "archivo" en el disco virtual es una entrada separada con el formato:
<nombre_del_archivo>::<contenido>

Funciones principales:
- listar_archivos()
- leer_archivo(nombre)
- escribir_archivo(nombre, contenido)
- borrar_archivo(nombre)
- formatear_disco()

"""
from pathlib import Path
from typing import List, Optional
import threading

DISCO_PATH = Path("disco_virtual.txt")
_disk_lock = threading.RLock()


def _ensure_disk_exists():
    if not DISCO_PATH.exists():
        DISCO_PATH.write_text("")


def _parse_disk() -> List[tuple]:
    """Devuelve lista de tuplas (nombre, contenido)"""
    _ensure_disk_exists()
    raw = DISCO_PATH.read_text()
    entries = []
    if not raw:
        return entries
    for line in raw.splitlines():
        if "::" not in line:
            continue
        name, content = line.split("::", 1)
        entries.append((name, content))
    return entries


def _write_disk(entries: List[tuple]):
    lines = [f"{name}::{content}" for name, content in entries]
    DISCO_PATH.write_text("\n".join(lines))


# API pública

def listar_archivos() -> List[str]:
    """Lista los nombres de archivos en el disco virtual."""
    with _disk_lock:
        return [name for name, _ in _parse_disk()]


def leer_archivo(nombre: str) -> Optional[str]:
    """Lee el contenido de un archivo, o devuelve None si no existe."""
    with _disk_lock:
        for name, content in _parse_disk():
            if name == nombre:
                return content
    return None


def escribir_archivo(nombre: str, contenido: str) -> None:
    """Crea o reemplaza un archivo en el disco virtual."""
    with _disk_lock:
        entries = _parse_disk()
        found = False
        for i, (name, _) in enumerate(entries):
            if name == nombre:
                entries[i] = (nombre, contenido)
                found = True
                break
        if not found:
            entries.append((nombre, contenido))
        _write_disk(entries)


def borrar_archivo(nombre: str) -> bool:
    """Borra un archivo. Devuelve True si se borró, False si no existía."""
    with _disk_lock:
        entries = _parse_disk()
        new_entries = [e for e in entries if e[0] != nombre]
        if len(new_entries) == len(entries):
            return False
        _write_disk(new_entries)
        return True


def formatear_disco() -> None:
    """Borra todo el disco virtual."""
    with _disk_lock:
        DISCO_PATH.write_text("")


if __name__ == "__main__":
    # demostración mínima al ejecutar directamente
    formatear_disco()
    escribir_archivo("hola.txt", "Hola desde el disco virtual")
    print(listar_archivos())
    print(leer_archivo("hola.txt"))

