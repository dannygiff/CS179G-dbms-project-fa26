#!/bin/bash
# nohup bash src/phase_2_metrics/run_benchmarks.sh > data/benchmark_log.txt 2>&1 &

TOPIC=cs179g_project_crawl_8f3k2
export PATH=/home/cs179g/miniconda3/envs/spark_env/bin:$PATH

notify() { curl -s -d "[benchmark] $1" "ntfy.sh/$TOPIC" > /dev/null; }

notify "Benchmarks started"

# three runs to average later
for run in 1 2 3; do
  # the 4 different file sizes
  # for file in data/cs2_10.jsonl data/cs2_25.jsonl data/cs2_50.jsonl data/cs2.jsonl; do
  for file in data/cs2_x2.jsonl; do
    # each file size gets the varying amount of workers. from docs... "local[k]: Run Spark locally with K worker threads (ideally, set this to the number of cores on your machine)."
    for cores in 1 2 3 4; do
      python src/phase_2_metrics/benchmark.py "local[$cores]" "$file"
    done
  done
  notify "Round $run of 3 done after $((SECONDS / 60)) min"
done

notify "Benchmarks finished after $((SECONDS / 60)) min"
