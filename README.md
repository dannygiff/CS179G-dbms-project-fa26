# CS179G Databases Project

## Usage

Activate the virtual environment with `conda activate spark_env`

## Proposal

Steam is a popular online video game marketplace that allows its users to write a review along with
their positive or negative recommendation. These reviews range from quality critiques and categorical
analysis to half-baked memes and frustrated libel. Steam itself will sometimes indicate that a game
has ”experienced a period of off-topic reviews” when a trend disrupts the ratio of positive to negative
reviews.

The goal of this project is to develop a categorization method that partitions these reviews into three
categories: quality, funny, and unsuccessful. Steam already provides community metadata for reviews,
including upvotes, downvotes, ”funny,” and emoji reactions. Our aim then is to collect and analyze
this data; looking for patterns within categories that we can later compare on different platforms like
Amazon or Airbnb.

### Phase 1
In this phase we plan to use a combination of Steam API keys and Scrapy to collect review data from
the Steam catalog. The keys are rate limited, so we will deploy a web crawler to supplement our data
as necessary.

### Phase 2
In phase 2 we use Spark to parse the raw data, taking advantage of vector stores for later integration
with Lucene. Spark’s distributed capabilities will be very useful considering the sheer volume of text
to parse.

### Phase 3
In phase 3 we build a web interface to explore, filter, and analyze our data. The page should offer
text searching across review bodies and visualization of calculated statistics, such as review sentiment
distribution and helpfulness ratios.