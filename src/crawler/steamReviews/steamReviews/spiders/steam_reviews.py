import scrapy
import json
import urllib.parse

class SteamReviewSpider(scrapy.Spider):
    name = "steam_reviews"
    allowed_domains = ["api.steampowered.com"]

    # we need this to avoid being redirected
    custom_settings = {
        'ROBOTSTXT_OBEY': False
    }

    def __init__(self, app_id=440, max_reviews=1, *args, **kwargs):
        # initialize parent class (scrapy Spider)
        # can use -a flag to pass in args for app_id and max_reviews
        super().__init__(*args, **kwargs)
        self.app_id = int(app_id)
        self.max_reviews = int(max_reviews)
        self.current_reviews = 0

    async def start(self):
        # self.logger.info(">>>>>>>>starting requests...")
        # the new steam review endpoint (thanks steam)
        base_url = "https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1"

        # interface requires a parameters json
        # https://partner.steamgames.com/doc/webapi/IUserReviewsService
        params = {
            "appid": self.app_id,
            "cursor": "*",
            "num_per_page": min(100, self.max_reviews), # 100/page limit
            "day_range": 0,
            "filter": 0, # 0 => Helpful, 1 => Recent, 2 => Updated, 3 => Funny
            "languages": ["english"],
        }
        request_params = {"input_json": json.dumps(params)}

        # build url, make request
        target_url = f"{base_url}?{urllib.parse.urlencode(request_params)}"
        yield scrapy.Request(
            url = target_url,
            callback = self.parse
        )

    def parse(self, response):
        # steam responds to the request with a status code
        if response.status != 200:
            self.logger.error(f"Request failed with code {response.status}")
            return

        # can itemize the yielded data here with json tags
        data = json.loads(response.text)

        response_data = data["response"]

        qs = response_data["query_summary"]
        if qs.get("total_reviews") is not None:
            tr = qs["total_reviews"]
            # self.logger.info(f">>>>>>>>>>>>> found total_reviews: {tr}")
            self.max_reviews = min(qs["total_reviews"], self.max_reviews)
        self.current_reviews += qs["num_reviews"]

        if response_data.get('reviews') is None:
            self.logger.info("response contained no reviews")
            return;

        yield from response_data["reviews"]

        if self.current_reviews < self.max_reviews:
            cursor = response_data["cursor"]
            params = {
                "appid": self.app_id,
                "cursor": cursor,
                "num_per_page": min(100, self.max_reviews - self.current_reviews),
                "day_range": 0,
                "filter": 0, # 0 => Helpful, 1 => Recent, 2 => Updated, 3 => Funny
                "languages": ["english"]
            }
            request_params = {"input_json": json.dumps(params)}
            base_url = "https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1"
            target_url = f"{base_url}?{urllib.parse.urlencode(request_params)}"
            yield scrapy.Request(
                url = target_url,
                callback = self.parse
            )
