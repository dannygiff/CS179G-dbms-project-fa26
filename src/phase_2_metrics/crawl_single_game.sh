#!/bin/bash
# nohup bash src/phase_2_metrics/crawl_single_game.sh [NAME] [APP_ID] [MAX_REVIEWS] > /dev/null 2>&1 &

NAME=${1:-cs2}
APP_ID=${2:-730} # default: counter strike 2
MAX_REVIEWS=${3:-500000}
TOPIC=cs179g_project_crawl_8f3k2
PROGRESS_EVERY=900
export PATH=/home/cs179g/miniconda3/envs/spark_env/bin:$PATH

OUT=$PWD/data/$NAME.jsonl
LOG=$PWD/data/crawl_$NAME.log

notify() { curl -s -d "[$NAME] $1" "ntfy.sh/$TOPIC" > /dev/null; }

notify "Crawl started: app $APP_ID, max $MAX_REVIEWS reviews"

cd src/crawler/steamReviews
scrapy crawl steam_reviews -O "$OUT" -a app_id="$APP_ID" -a max_reviews="$MAX_REVIEWS" > "$LOG" 2>&1 &
# save the process
PID=$!

LAST=0
# while process is still running
while kill -0 $PID 2> /dev/null; do
  sleep 10
  # send progress every 15 min
  if (( SECONDS - LAST >= PROGRESS_EVERY )); then
    notify "Progress: $(wc -l < "$OUT") / $MAX_REVIEWS reviews after $((SECONDS / 60)) min"
    LAST=$SECONDS
  fi
done

notify "Crawl ended after $((SECONDS / 60)) min: $(wc -l < "$OUT") reviews, $(grep -c ERROR "$LOG") errors"
