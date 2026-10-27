cd crawler/steamReviews/

echo "[" > top100.json
while read p; do
  # scrapy crawl steam_reviews -O output.json -a max_reviews=1 -a app_id=$p
  sed '2!d;s/1/hi/g' test.json >> top100.json
  # echo "," >> top100.json
done <test.json
echo "]" >> top100.json

# scrapy crawl steam_reviews -O test.json -a max_reviews=1 -a app_id=$p