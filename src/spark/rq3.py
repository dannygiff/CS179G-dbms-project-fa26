import matplotlib
import pandas
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# use when standalone
#
# spark = (
#     SparkSession.builder.appName("Phase2 Research Questions")
#     .config("spark.driver.memory", "8g")
#     .config("spark.executor.memory", "8g")
#     .config("spark.sql.debug.maxToStringFields", "100")
#     .getOrCreate()
# )

# labeled_reviews_path = "/home/cs179g/repo/data/labeled_reviews.parquet"
# labeled_reviews = spark.read.format("parquet").load(labeled_reviews_path)

topics = [
    "-1_game_vkcombagosi_play_good",
    "0_game_good_play_fun",
    "1_russian_russians_game_learn",
    "2_shooter_shoot_person_aim",
    "3_1010_r8_m8_88",
    "4_gotta_mom_gay_fast",
    "5_16_update_game_updates",
    "6_knife_gamble_cases_gambling",
    "7_gud_veri_gg_ez",
    "8_cs_10_16_offensive",
    "9_review_badge_doing_steam",
    "10_cyka_blyat_rush_syka",
    "11_smurfs_smurf_hackers_game",
    "12_valorant_better_game_play",
    "13_bugs_average_grind_story",
    "14_chickens_chicken_kill_1010",
    "15_surf_surfing_fun_bhop",
    "16_pew_pewpew_pow_pewpewpew",
    "17_volvo_fix_pls_game",
    "18_awp_1010_awps_awped",
    "19_anticheat_fix_better_needs",
    "20_relationship_lovehate_hate_abusive",
    "21_h1_strike_game_spoiler",
]


def rq3(labeled_reviews):
    properties = {"user": "root", "driver": "com.mysql.cj.jdbc.Driver"}

    labeled_reviews.select(
        "topic_name", "post_review_playtime", "playtime_forever", "playtime_at_review"
    ).groupby("topic_name").agg(
        F.count("post_review_playtime").alias("count"),
        F.avg("playtime_forever").alias("avg_playtime_forever"),
        F.avg("playtime_at_review").alias("avg_playtime_before"),
        F.avg("post_review_playtime").alias("avg_playtime_after"),
        F.avg(F.col("playtime_at_review") / F.col("playtime_forever")).alias(
            "avg_review_timing"
        ),
    ).write.jdbc(
        url="jdbc:mysql://127.0.0.1:3306/steamReviews",
        table="rq3_data",
        mode="overwrite",
        properties=properties,
    )

    for i in range(0, len(topics)):
        filtered_reviews = labeled_reviews.filter(f"topic_name == '{topics[i]}'")
        pddf = pandas.DataFrame(
            filtered_reviews.withColumn(
                "review_timing", F.col("playtime_at_review") / F.col("playtime_forever")
            )
            .select("review_timing")
            .filter("review_timing <= 1")
            .collect()
        )
        ax = pddf.plot.hist(bins=100, title=f"Review Timings for {topics[i]}")
        ax.set_xlabel("ratio of playtime before reviewing")
        fig = ax.get_figure()
        fig.savefig(f"./data/topic{i - 1}_review_timings.png")
        matplotlib.pyplot.close(fig)


# rq3(labeled_reviews)
