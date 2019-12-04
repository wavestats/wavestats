from urllib import request
from frames_to_timecode import frames_to_timecode


def get_level_url(in_search_string, in_file):
    search_index = in_file.find(in_search_string)
    url_end = in_file.rfind(b"url>", 0, search_index) - 2
    url_start = in_file.rfind(b"url>", 0, url_end) + 4
    url = in_file[url_start:url_end]
    return url.decode()  # if we leave as bytes, it crashes urlopen in get_scores_from_level


def get_scores_from_level(in_level_url, in_steam_key):  # gets user and WR score
    level_file = request.urlopen(in_level_url).read()
    best_score_start = level_file.find(b"score>") + 6
    best_score_end = level_file.find(b"score>", best_score_start) - 2
    best_score = level_file[best_score_start:best_score_end]
    id_index = level_file.find(in_steam_key)
    if id_index == -1:  # indicates steamkey not found, i.e. coin or speed time not in record
        user_score = b"inf"
        rank = b"inf"
    else:
        user_score_start = level_file.find(b"score>", id_index) + 6
        user_score_end = level_file.find(b"</score", id_index)
        user_score = level_file[user_score_start:user_score_end]
        rank_start = level_file.find(b"rank>", id_index) + 5
        rank_end = level_file.find(b"</rank", id_index)
        rank = level_file[rank_start:rank_end]
    user_seconds = frames_to_timecode(user_score, True)
    best_seconds = frames_to_timecode(best_score, True)
    return {"user_score": user_score, "best_score": best_score,
            "user_seconds": user_seconds, "best_seconds": best_seconds, "rank": rank}


def get_scores_from_steamkey(steamkey, category):  # steam key should be a bytes string
    if category == b"combined":
        speed_scores = get_scores_from_steamkey(steamkey, b"Speed")
        coin_scores = get_scores_from_steamkey(steamkey, b"Coin")
        speed_user_scores = [score["user_score"] for score in speed_scores]
        coin_user_scores = [score["user_score"] for score in coin_scores]
        speed_wrs = [score["best_score"] for score in speed_scores]
        coin_wrs = [score["best_score"] for score in coin_scores]

        best_scores = []
        for speed_pb, coin_pb, speed_wr, coin_wr in zip(speed_user_scores, coin_user_scores, speed_wrs, coin_wrs):
            user_score = str(min(float(speed_pb), float(coin_pb))).encode()
            best_score = str(min(float(speed_wr), float(coin_wr))).encode()
            user_seconds = frames_to_timecode(user_score, True)
            best_seconds = frames_to_timecode(best_score, True)
            dict_to_append = {"user_score": user_score, "best_score": best_score,
                              "user_seconds": user_seconds, "best_seconds": best_seconds, "rank": b"inf"}
            best_scores.append(dict_to_append)
        return best_scores

    category = category.title().decode()  # capitalizes first letter
    master_file = request.urlopen("https://steamcommunity.com/stats/532170/leaderboards/0/?xml=1").read()
    if category == "Dark":
        search_strings = [f"World {world} Level {level} {category}".encode() for
                          world in range(1, 6) for level in range(1, 7)]
    else:
        search_strings = [f"World {world} Level {level} {category}".encode() for
                          world in range(1, 7) for level in range(1, 7)]
    level_urls = [get_level_url(search_string, master_file) for search_string in search_strings]
    scores = [get_scores_from_level(level_url, steamkey) for level_url in level_urls]
    return scores
