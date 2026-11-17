
import os
from glob import glob
from collections import Counter
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

dataset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")

comm.Barrier()
total_start = MPI.Wtime()

if rank == 0:
    with open(os.path.join(dataset_dir, "consulta.txt"), "r", encoding="utf-8") as f:
        consulta = set(line.strip().lower() for line in f if line.strip())
    archivos = sorted(glob(os.path.join(dataset_dir, "file_*.txt")))
else:
    consulta = None
    archivos = None

consulta = comm.bcast(consulta, root=0)

if rank == 0:
    frecuencias = Counter()
    total_archivos = 0
    total_tokens = 0
    tiempos = {0: 0.0}

    pendientes = iter(archivos)
    activos = 0

    for proceso in range(1, size):
        archivo = next(pendientes, None)
        comm.send(archivo, dest=proceso, tag=1)
        if archivo is not None:
            activos += 1

    finalizados = 0

    while finalizados < size - 1:
        estado = MPI.Status()
        mensaje = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=estado)
        proceso = estado.Get_source()

        if estado.Get_tag() == 2:
            freq, tokens = mensaje
            frecuencias.update(freq)
            total_archivos += 1
            total_tokens += tokens

            siguiente = next(pendientes, None)
            comm.send(siguiente, dest=proceso, tag=1)

        else:
            cantidad, tiempo = mensaje
            tiempos[proceso] = tiempo
            finalizados += 1

    total_time = MPI.Wtime() - total_start
    tiempos[0] = total_time
    for proceso in range(size):
        print(f"Proceso {proceso}: tiempo local: {tiempos.get(proceso, 0):.6f} segundos")

    print(f"\nArchivos procesados: {total_archivos}")
    print(f"Total de tokens leidos: {total_tokens}")
    print(f"Total de ocurrencias encontradas: {sum(frecuencias.values())}")
    print("\nTop 10 palabras de consulta en el corpus:")

    for palabra, cuenta in frecuencias.most_common(10):
        print(f"  {palabra}: {cuenta}")

    print(f"\nEXECUTION_TIME={total_time:.6f}")

else:
    local_start = MPI.Wtime()
    frecuencias = Counter()
    tokens = 0
    cantidad = 0

    while True:
        ruta = comm.recv(source=0, tag=1)

        if ruta is None:
            break

        local_freq = Counter()

        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                palabras = [w.lower() for w in linea.split()]
                tokens += len(palabras)

                for palabra in palabras:
                    if palabra in consulta:
                        local_freq[palabra] += 1

        frecuencias.update(local_freq)
        cantidad += 1
        comm.send((dict(local_freq), len(palabras) if False else 0), dest=0, tag=99) if False else None
        comm.send((dict(local_freq), tokens), dest=0, tag=2)
        tokens = 0

    local_time = MPI.Wtime() - local_start
    comm.send((cantidad, local_time), dest=0, tag=3)

