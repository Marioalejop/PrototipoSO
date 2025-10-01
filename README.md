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
Comando (ES)	            Alias clásicos	    Descripción
ayuda	                    help	            Muestra ayuda.
listar	                    ls	                Lista archivos del disco virtual.
ver <archivo>	            cat <archivo>	    Muestra contenido.
escribir <archivo> "texto"	write	            Crea/sobrescribe con el texto indicado.
borrar <archivo>	        rm	                Elimina el archivo.
formatear	                            	    Limpia el sistema de archivos virtual.
ejecutar [nombre]	        run	                Crea un proceso con nombre (por defecto demo).
procesos	                ps	                Lista procesos (running + ready si está implementado).
terminar <pid>	            kill <pid>	        Finaliza un proceso.
memoria	                    memstat	            Estadísticas/estado de frames.
salir	                    exit, quit	        Cierra la sesión de shell.

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

