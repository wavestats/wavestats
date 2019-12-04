from urllib import request
from get_scores import get_level_url
import xml.etree.ElementTree as Et
import itertools


def get_all_keys_from_level_xml(in_xml):
    entries = in_xml[-1]
    all_ids = [entry[0].text for entry in entries]  # entry[0] is the steam id tag in the xml, .text gets the id in tag
    return all_ids


def remove_players_not_beat_all_levels(players, speed_level_search_strings, coin_level_search_strings):
    master_file = request.urlopen("https://steamcommunity.com/stats/532170/leaderboards/0/?xml=1").read()
    speed_level_urls = [get_level_url(search_string, master_file) for search_string in speed_level_search_strings]
    coin_level_urls = [get_level_url(search_string, master_file) for search_string in coin_level_search_strings]
    speed_level_files = [request.urlopen(level_url).read() for level_url in speed_level_urls]
    coin_level_files = [request.urlopen(level_url).read() for level_url in coin_level_urls]
    speed_level_xmls = [Et.fromstring(level_file) for level_file in speed_level_files]
    coin_level_xmls = [Et.fromstring(level_file) for level_file in coin_level_files]

    for speed_xml, coin_xml in zip(speed_level_xmls, coin_level_xmls):
        all_speed_xml_keys = get_all_keys_from_level_xml(speed_xml)
        all_coin_xml_keys = get_all_keys_from_level_xml(coin_xml)
        for player in players:
            if player not in all_speed_xml_keys and player not in all_coin_xml_keys:
                players.remove(player)

    return players


def get_players_finished_game():
    master_file = request.urlopen("https://steamcommunity.com/stats/532170/leaderboards/0/?xml=1").read()
    world_6_speed_search_strings = [f"World 6 Level {level} Speed".encode() for level in range(1, 7)]
    world_6_coin_search_strings = [f"World 6 Level {level} Coin".encode() for level in range(1, 7)]
    world_6_search_strings = world_6_speed_search_strings + world_6_coin_search_strings
    world_6_level_urls = [get_level_url(search_string, master_file) for search_string in world_6_search_strings]
    world_6_level_files = [request.urlopen(level_url).read() for level_url in world_6_level_urls]
    world_6_level_xmls = [Et.fromstring(world_6_level_file) for world_6_level_file in world_6_level_files]
    # line below makes list of lists, which we must flatten (i.e. make into 1 list)
    world_6_keys_with_duplicates = [get_all_keys_from_level_xml(xml) for xml in world_6_level_xmls]
    world_6_keys_with_duplicates = list(itertools.chain(*world_6_keys_with_duplicates))  # Flattens list
    world_6_keys = list(set(world_6_keys_with_duplicates))
    players_finished_game = remove_players_not_beat_all_levels(world_6_keys, world_6_speed_search_strings,
                                                               world_6_coin_search_strings)
    return players_finished_game  # contains all players who finished game (i.e. completed all world 6 levels)
