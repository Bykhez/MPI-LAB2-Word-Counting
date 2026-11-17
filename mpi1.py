
import os
import time
from glob import glob
from collections import Counter
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_dir = os.path.join(script_dir, "dataset")

comm.Barrier()
total_start = MPI.Wtime()

if rank == 0:
    consulta_path = os.path.join(dataset_dir, "consulta.txt")

    with open(consulta_path, "r", encoding="utf-8") as f:
        consulta = set(line.strip().lower() for line in f if line.strip())

    archivos = sorted(glob(os.path.join(dataset_dir, "file_*.txt")))

    bloques = []
    base = len(archivos) // size
    extra = len(archivos) % size
    inicio = 0

    for i in range(size):
        cantidad = base + (1 if i < extra else 0)
        bloques.append(archivos[inicio:inicio + cantidad])
        inicio += cantidad
else:
    consulta = None
    bloques = None

consulta = comm.bcast(consulta, root=0)
mis_archivos = comm.scatter(bloques, root=0)

local_start = MPI.Wtime()

frecuencias = Counter()
tokens = 0

for ruta in mis_archivos:
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            palabras = linea.split()
            palabras = [w.lower() for w in palabras]
            tokens += len(palabras)

            for palabra in palabras:
                if palabra in consulta:
                    frecuencias[palabra] += 1

local_time = MPI.Wtime() - local_start

resultados = comm.gather(
    (dict(frecuencias), len(mis_archivos), tokens, local_time),
    root=0
)

if rank == 0:
    global_freq = Counter()
    total_archivos = 0
    total_tokens = 0

    for i, (freq, cantidad, num_tokens, tiempo) in enumerate(resultados):
        global_freq.update(freq)
        total_archivos += cantidad
        total_tokens += num_tokens

        print(f"Proceso {i}: {cantidad} archivos, tiempo local: {tiempo:.6f} segundos")

    total_time = MPI.Wtime() - total_start

    print(f"\nArchivos procesados: {total_archivos}")
    print(f"Total de tokens leidos: {total_tokens}")
    print(f"Total de ocurrencias encontradas: {sum(global_freq.values())}")
    print("\nTop 10 palabras de consulta en el corpus:")

    for palabra, cuenta in global_freq.most_common(10):
        print(f"  {palabra}: {cuenta}")

    print(f"\nEXECUTION_TIME={total_time:.6f}")
