\# Parallel Word Counting in a Text Corpus with MPI



\## 1. Problem Description



The objective of this project is to count the occurrences of a set of query words in a large text corpus using parallel processing with MPI.



The dataset contains a file named `consulta.txt`, which stores the words to search for, and multiple text files named `file\_XXXX.txt`, which form the corpus.



The project implements and evaluates two parallel strategies:



\- \*\*MPI Version 1:\*\* Static distribution of files among processes.

\- \*\*MPI Version 2:\*\* Dynamic distribution of files to improve load balancing.



Both implementations must produce the same global word counts and Top 10 results as the sequential baseline.



\## 2. Environment and Execution Instructions



\### Environment



The project was developed using:



\- Operating System: Windows 11

\- MPI environment: Docker container

\- Docker image: `augustosalazar/slim-mpi:2`

\- Programming language: Python 3

\- MPI library: mpi4py

\- Number of MPI processes for the experiments: 13



\### 3.1 Experimental Plan



The experiment follows these steps:



1\. Generate the text corpus using the provided `generator.py`.

2\. Execute the sequential baseline and record its execution time and Top 10 results.

3\. Execute MPI Version 1 using 13 processes.

4\. Perform three runs and record total execution time and local processing times.

5\. Calculate average execution time, speedup, efficiency, and load imbalance ratio (LI).

6\. Execute MPI Version 2 using the same number of processes.

7\. Repeat the three-run experiment and compare both implementations.



\### 3.2 Sequential Baseline



The provided `baseline\_secuencial.py` is used without modifications.



It reads the query words from `consulta.txt`, scans all corpus files, counts the occurrences of each query word, and displays the ten most frequent words.



To execute the baseline:



```bash

docker run --rm -v "%cd%:/app" augustosalazar/slim-mpi:2 python /app/baseline\_secuencial.py

```



\### 3.3 MPI Version 1



The first MPI implementation uses static file distribution.



Its operation is:



1\. Process 0 reads the query words from `consulta.txt`.

2\. The query words are broadcast to all processes using `comm.bcast`.

3\. Process 0 obtains the list of corpus files.

4\. The files are distributed statically among the processes using `comm.scatter`.

5\. Each process counts the occurrences of query words in its assigned files.

6\. Partial results are collected using `comm.gather`.

7\. Process 0 combines the results and displays the global Top 10.



Each process reports its number of assigned files and local processing time.



\### 3.4 Test Procedure



First, generate the dataset:



```bash

docker run --rm -v "%cd%:/app" augustosalazar/slim-mpi:2 python /app/generator.py

```



Execute MPI Version 1:



```bash

docker run --rm -v "%cd%:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --oversubscribe -n 13 python /app/mpi1.py

```



Execute MPI Version 2:



```bash

docker run --rm -v "%cd%:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --oversubscribe -n 13 python /app/mpi2.py

```



Each MPI implementation was executed three times using the same dataset and number of processes.



\## 4. Experimental Plan Execution



\### 4.1 Sequential Baseline Timing



The sequential implementation was executed using the generated dataset.



| Metric | Result |

|---|---:|

| Number of files | 3,000 |

| Total tokens | 44,951,458 |

| Total occurrences | 3,631,778 |

| Execution time (T\_seq) | 27.466270 seconds |



The Top 10 results were:



| Word | Occurrences |

|---|---:|

| a | 785,774 |

| para | 392,156 |

| sus | 228,913 |

| otros | 105,530 |

| ante | 99,832 |

| unos | 88,794 |

| otra | 83,901 |

| vosotros | 61,617 |

| mios | 58,420 |

| tuya | 56,635 |



Both MPI implementations produced the same Top 10 results as the sequential baseline.



\### 4.2 MPI Version 1 Timing Results



MPI Version 1 was executed three times using 13 processes.



\*\*Total execution times:\*\*



| Run | Execution time (seconds) |

|---|---:|

| 1 | 6.523256 |

| 2 | 5.480536 |

| 3 | 5.542491 |

| Average (T\_p) | 5.848761 |



\*\*Local processing times per process:\*\*



| Process | Run 1 (s) | Run 2 (s) | Run 3 (s) |

|---|---:|---:|---:|

| 0 | 6.444413 | 5.419991 | 5.464963 |

| 1 | 6.330851 | 5.250710 | 5.072153 |

| 2 | 5.654351 | 4.232576 | 4.142426 |

| 3 | 6.485060 | 5.338829 | 5.408994 |

| 4 | 5.857732 | 4.829346 | 4.590354 |

| 5 | 6.388826 | 4.986225 | 5.043557 |

| 6 | 6.444108 | 5.023388 | 4.951765 |

| 7 | 6.097167 | 4.788888 | 4.990930 |

| 8 | 6.337522 | 5.328856 | 5.144430 |

| 9 | 6.092513 | 4.956955 | 4.897767 |

| 10 | 5.792364 | 4.762443 | 4.416929 |

| 11 | 6.045342 | 4.714419 | 4.532369 |

| 12 | 6.435950 | 5.201431 | 5.132276 |



\*\*Performance metrics:\*\*



The speedup is calculated as:



S\_p = T\_seq / T\_p



The efficiency is calculated as:



E\_p = S\_p / p



Where p = 13.



| Metric | Result |

|---|---:|

| Sequential time | 27.466270 s |

| Average MPI1 time | 5.848761 s |

| Speedup | 4.6961x |

| Efficiency | 36.12% |



\### 4.3 Load Imbalance Evidence (MPI Version 1)



The load imbalance ratio is calculated as:



LI = max(t\_i) / mean(t\_i)



The results for the three MPI1 runs were:



| Run | Maximum local time (s) | Mean local time (s) | LI |

|---|---:|---:|---:|

| 1 | 6.485060 | 6.185092 | 1.0485 |

| 2 | 5.419991 | 4.987235 | 1.0868 |

| 3 | 5.464963 | 4.906839 | 1.1137 |

| Average | — | — | 1.0830 |



These results show that the static distribution produced some load imbalance. The local processing times varied between processes because the input files have different sizes. Some processes therefore finished earlier than others.



\### 4.4 MPI Version 2: Load-Balancing Improvement



MPI2 uses dynamic scheduling. Instead of assigning a fixed group of files to each process, the root process assigns another file to a worker whenever it finishes its current file.



The root process acts as the coordinator, while processes 1 to 12 perform the file-processing tasks.



\*\*Total execution times:\*\*



| Run | Execution time (seconds) |

|---|---:|

| 1 | 5.411368 |

| 2 | 5.371442 |

| 3 | 6.008160 |

| Average (T\_p) | 5.596990 |



\*\*Local processing times per process:\*\*



| Process | Run 1 (s) | Run 2 (s) | Run 3 (s) |

|---|---:|---:|---:|

| 0 (Coordinator) | 5.411368 | 5.371442 | 6.008160 |

| 1 | 5.340934 | 5.271000 | 5.852195 |

| 2 | 5.393780 | 5.275236 | 5.867590 |

| 3 | 5.340939 | 5.270671 | 5.861435 |

| 4 | 5.370572 | 5.280007 | 5.879897 |

| 5 | 5.334773 | 5.286971 | 5.862949 |

| 6 | 5.391264 | 5.275044 | 5.967573 |

| 7 | 5.345482 | 5.354528 | 5.867790 |

| 8 | 5.328489 | 5.337139 | 5.849994 |

| 9 | 5.331204 | 5.278746 | 5.922487 |

| 10 | 5.329394 | 5.291616 | 5.879635 |

| 11 | 5.326320 | 5.275175 | 5.901521 |

| 12 | 5.378032 | 5.320803 | 5.862036 |



For the MPI2 load imbalance calculation, only worker processes (ranks 1 to 12) were considered, because rank 0 acts as the coordinator and distributes files rather than processing them.



\*\*Load imbalance results:\*\*



| Run | LI (worker processes) |

|---|---:|

| 1 | 1.0080 |

| 2 | 1.0116 |

| 3 | 1.0147 |

| Average | 1.0114 |



\*\*MPI2 performance metrics:\*\*



| Metric | Result |

|---|---:|

| Sequential time | 27.466270 s |

| Average MPI2 time | 5.596990 s |

| Speedup | 4.9073x |

| Efficiency | 37.75% |

| Average LI | 1.0114 |



MPI2 reduced the average load imbalance compared with MPI1. Its average execution time was also lower, decreasing from 5.848761 seconds to 5.596990 seconds.



\## 5. Analysis



\### 5.1 Parallel Performance



MPI1 improved performance compared with the sequential baseline. The sequential execution time was 27.466270 seconds, while MPI1 achieved an average execution time of 5.848761 seconds, resulting in a speedup of 4.6961x.



This is below the ideal speedup of 13. The difference can be explained by communication overhead, file input/output operations, process coordination, and load imbalance.



\### 5.2 Load Balance



MPI1 showed load imbalance because files had different sizes and were distributed statically. Its average LI was 1.0830.



MPI2 improved load distribution through dynamic scheduling. Its average worker LI was 1.0114, which is closer to the ideal value of 1.0.



MPI2 also achieved a lower average execution time of 5.596990 seconds, representing a modest performance improvement over MPI1.



\### 5.3 Limitations



The experiment was performed in a containerized environment, where file input/output, communication overhead, and available computational resources may affect execution times.



Only three runs were performed for each MPI implementation, so the results may vary between executions. The number of processes was also fixed at 13, meaning that other process configurations were not evaluated.



Despite these limitations, the results consistently show that MPI2 achieved better load balance and a slightly lower average execution time.



\## 6. Conclusions



The dynamic distribution strategy used in MPI2 is recommended for this problem. Compared with MPI1, it reduced the average execution time from 5.848761 to 5.596990 seconds and improved the speedup from 4.6961x to 4.9073x, with efficiency increasing from 36.12% to 37.75%. It also reduced the average load imbalance ratio from 1.0830 to 1.0114. These results indicate that dynamically assigning files to available workers is more suitable when input files have different sizes.

