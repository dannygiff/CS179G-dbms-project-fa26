cd /home/cs179g/working/tomatopaster/CS179G-dbms-project-fa26/data

echo "[" > top100.json
while read p; do
  # scrapy crawl steam_reviews -O output.json -a max_reviews=1 -a app_id=$p
  cd /home/cs179g/working/tomatopaster/CS179G-dbms-project-fa26/data
  echo "{\"app_id\": $p," >> top100.json
  echo "\"response\": [" >> top100.json
  sed '1d;$d' steam_reviews.json >> top100.json
  echo "]}," >> top100.json
done <test.txt
echo "]" >> top100.json

# scrapy crawl steam_reviews -O test.json -a max_reviews=1 -a app_id=$p