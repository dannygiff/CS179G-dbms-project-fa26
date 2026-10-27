# Crawls reviews for every app id in ID_FILE and combines them into FINAL_FILE.
# To test in your own folder, change BASE (and ID_FILE / MAX_REVIEWS) below.

# ---- settings: change these ----
BASE=/home/cs179g/repo                         # root of the project checkout
ID_FILE=$BASE/data/top_seller_app_ids.txt      # app ids to crawl, one per line
MAX_REVIEWS=10000                              # reviews per game
export PATH=/home/cs179g/miniconda3/envs/spark_env/bin:$PATH

# ---- derived paths: no need to change ----
DATA_DIR=$BASE/data
CRAWLER_DIR=$BASE/src/crawler/steamReviews     # scrapy must be run from here
OUTPUT_FILE=$DATA_DIR/output.json              # one game's reviews (overwritten each loop)
FINAL_FILE=$DATA_DIR/top100.json               # all games combined

cd "$CRAWLER_DIR"

echo "[" > "$FINAL_FILE"
while read p; do
  rm -f "$OUTPUT_FILE"                         # so a failed crawl can't reuse the last game's file
  scrapy crawl steam_reviews -O "$OUTPUT_FILE" -a max_reviews=$MAX_REVIEWS -a app_id=$p
  echo "{\"app_id\": $p," >> "$FINAL_FILE"
  echo "\"response\": [" >> "$FINAL_FILE"
  sed '1d;$d' "$OUTPUT_FILE" >> "$FINAL_FILE"
  echo "]}," >> "$FINAL_FILE"
done < "$ID_FILE"
sed -i '$ s/,$//' "$FINAL_FILE"                # turn the last "]}," into "]}"
echo "]" >> "$FINAL_FILE"                      # close the list
