***Descripción**

Prototipo didáctico de un sistema operativo simplificado con:

Procesos: creación/terminación y planificación round-robin.

Memoria: visualización por frames (libre/ocupado).

Sistema de archivos: disco virtual con listar/leer/escribir/borrar/formatear.

Shell: intérprete de comandos (en español y alias clásicos).

GUI (Tkinter): consola integrada, barra de acciones y vista de memoria.

Objetivo: apoyar prácticas de SO y preparar la sustentación con demos reproducibles.


***Arquitectura***

Flujo principal: Usuario → GUI (Tkinter) → Shell → {Procesos, Memoria, Archivos}.

main.py inicializa los módulos y ejecuta CLI o GUI (--gui).

sincronizacion.py (opcional) ofrece primitivos (Semáforo/Mutex).


**Diaigrama de Procesos**

graph LR
  U[Usuario] -->|Entrada/Salida| GUI[GUI (Tkinter)]
  M[main.py] -->|--gui| GUI
  M -->|CLI| SH[Shell]

  GUI -->|ejecutar línea| SH

  SH -->|run/ps/kill| PR[Procesos\nRR + cola READY]
  SH -->|memstat/...| ME[Memoria\nframes fijos]
  SH -->|ls/cat/write/rm| FS[Archivos\nDisco virtual]

  FS --> DV[(disco_virtual.txt)]

  SY[Sincronización\nSemáforo/Mutex] -.-> PR



***Requisitos***

Python 3.9+ (recomendado 3.10/3.11).

Tkinter (viene con Python estándar en Windows/macOS; en Linux puede requerir sudo apt install python3-tk).

Trabajo colaborativo con el versionamiento de repositorio en GiutHub 

Sin dependencias externas para el prototipo básico.


**Comandos disponibles**
Comandos disponibles:
 - ayuda       Muestra la lista de comandos disponibles y su descripción.
 - borrar      Elimina un archivo del disco virtual. Uso: borrar <archivo>
 - cat         Muestra el contenido de un archivo. Uso: cat <archivo>
 - crearproceso Crea y ejecuta un proceso de ejemplo. Uso: crearproceso <nombre_proceso>
 - ejecutar    Crea y ejecuta un proceso de ejemplo. Uso: ejecutar <nombre_proceso>
 - eliminar    Elimina un archivo del disco virtual. Uso: eliminar <archivo>
 - escribir    Crea o sobrescribe un archivo. Uso: escribir <archivo> <contenido>
 - exit        Cierra el shell.
 - formatear   Borra todos los archivos del disco virtual.
 - help        Muestra la lista de comandos disponibles y su descripción.
 - kill        Termina un proceso por su PID. Uso: kill <pid>
 - lista       Lista los archivos en el disco virtual.
 - listar      Lista los archivos en el disco virtual.
 - ls          Lista los archivos en el disco virtual.
 - memoria     Muestra estadísticas de la memoria principal.
 - memstat     Muestra estadísticas de la memoria principal.
 - mostrar     Muestra el contenido de un archivo. Uso: mostrar <archivo>
 - procesos    Muestra la lista de procesos en ejecución.
 - ps          Muestra la lista de procesos en ejecución.
 - rm          Elimina un archivo del disco virtual. Uso: rm <archivo>
 - run         Crea y ejecuta un proceso de ejemplo. Uso: run <nombre_proceso>
 - salir       Cierra el shell.
 - terminar    Termina un proceso por su PID. Uso: terminar <pid>
 - ver         Muestra el contenido de un archivo. Uso: ver <archivo>
 - write       Crea o sobrescribe un archivo. Uso: write <archivo> <contenido>

**Estructura del proyecto**

.
├─ main.py                # Punto de entrada (CLI/GUI)
├─ gui.py                 # Interfaz Tkinter (terminal + botones + memoria)
├─ shell.py               # Intérprete de comandos y mapeo ES/alias
├─ procesos.py            # Gestor de procesos: cola READY + RR
├─ memoria.py             # Frames y estadísticas
├─ archivos.py            # Disco virtual: listar/leer/escribir/borrar/formatear
├─ sincronizacion.py      # (Opcional) Semáforo/Mutex para rutinas de sincronización
└─ docs/
   └─ Arquitectura_PrototipoSO.drawio  # Diagrama editable (opcional)


**GUI: atajos y botones**

Atajos:

F1 → ayuda

Ctrl+Enter → ejecutar línea

Ctrl+L → limpiar consola

F5 → refrescar vista de Memoria

Barra de acciones:

Archivos: Escribir, Ver, Borrar (con campos Archivo y Texto).

Procesos: Ejecutar proceso, Procesos, Terminar PID.

Utilidades: Listar (ls), Formatear, Memoria.

