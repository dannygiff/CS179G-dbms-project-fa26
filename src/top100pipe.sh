cd /home/cs179g/repo/data

echo "[" > top100.json
while read p; do
  cd /home/cs179g/repo/src/crawler/steamReviews
  scrapy crawl steam_reviews -O /home/cs179g/repo/data/output.json -a max_reviews=10000 -a app_id=$p
  cd /home/cs179g/repo/data
  echo "{\"app_id\": $p," >> top100.json
  echo "\"response\": [" >> top100.json
  sed '1d;$d' output.json >> top100.json
  echo "]}," >> top100.json
done </home/cs179g/repo/data/top_seller_app_ids.txt
sed -i '$ s/,$//' top100.json  # turn the last "]}," into "]}"
echo "]" >> top100.json        # close the list

# Change the paths to your own, comment out above (for testing in your own folder)

# cd /home/cs179g/working/whore_hey/CS179G-dbms-project-fa26/data

# echo "[" > top100.json
# while read p; do
#   cd /home/cs179g/working/whore_hey/CS179G-dbms-project-fa26/src/crawler/steamReviews
#   scrapy crawl steam_reviews -O /home/cs179g/working/whore_hey/CS179G-dbms-project-fa26/data/output.json -a max_reviews=1 -a app_id=$p
#   cd /home/cs179g/working/whore_hey/CS179G-dbms-project-fa26/data
#   echo "{\"app_id\": $p," >> top100.json
#   echo "\"response\": [" >> top100.json
#   sed '1d;$d' output.json >> top100.json
#   echo "]}," >> top100.json
# done </home/cs179g/working/whore_hey/CS179G-dbms-project-fa26/data/three_ids.txt
# sed -i '$ s/,$//' top100.json  # turn the last "]}," into "]}"
# echo "]" >> top100.json        # close the list