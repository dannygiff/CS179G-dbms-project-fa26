import scrapy

# FluXion129

class TopSellersSpider(scrapy.Spider):
    name = "top_sellers"
    # this only gets the top 100 selling games
    # was thinking it would be at least a bit useful & relatively easy = good practice
    start_urls = [
        "https://store.steampowered.com/charts/topselling/US"
    ]

    def parse(self, response):
        # they clearly use some kind of class generator, but it is consistent across reloads
        for game in response.xpath("//a[@class='OPsTpFowVcA- Focusable']"):
            yield {
                "link": game.attrib["href"],
                "name": game.css("div.vGOJiIhBnNo-::text").get(),
            }

        # use the next page button to find the next page to scrape
        # next_page = response.css("li.next a::attr(href)").get()
        # if next_page is not None:
        #     next_page = response.urljoin(next_page)
        #     yield scrapy.Request(next_page, callback=self.parse)
