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

    def __init__(self, app_id=440, *args, **kwargs):
        # initialize parent class (scrapy Spider)
        # can use -a flag to pass in args for app_id and max_reviews
        super().__init__(*args, **kwargs)
        self.app_id = int(app_id)
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
            "num_per_page": 100,
            "day_range": 0,
            "filter": 1, # 0 => Helpful, 1 => Recent, 2 => Updated, 3 => Funny
            "purchase_type": 1, # 0 => Steam only, 1 => All, 2 => Non-Steam only
            "filter_offtopic_activity": "false",
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

        if response_data.get('reviews') is None:
            self.logger.info("response contained no reviews, quitting")
            return;

        yield from response_data["reviews"]

        # create next request
        cursor = response_data["cursor"]
        params = {
            "appid": self.app_id,
            "cursor": cursor,
            "num_per_page": 100,
            "day_range": 0,
            "filter": 1, # 0 => Helpful, 1 => Recent, 2 => Updated, 3 => Funny
            "purchase_type": 1, # 0 => Steam only, 1 => All, 2 => Non-Steam only
            "filter_offtopic_activity": "false",
            "languages": ["english"]
        }
        request_params = {"input_json": json.dumps(params)}
        base_url = "https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1"
        target_url = f"{base_url}?{urllib.parse.urlencode(request_params)}"
        yield scrapy.Request(
            url = target_url,
            callback = self.parse
        )
