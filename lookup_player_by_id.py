from urllib import request
import json

# INPUT YOUR OWN STEAM KEY WHERE IT SAYS {steam_key}


def lookup_players_by_id(players_list):  # returns dict with {playername: steamkey}
    base_url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?" \
               "key={steam_key}&steamids="
    max_players_per_request = 100
    # Line below produces list of lists where each list is no longer than max_players_per_request
    split_players_list = [players_list[i * max_players_per_request:(i + 1) * max_players_per_request] for i in
                          range((len(players_list) + max_players_per_request - 1) // max_players_per_request)]
    comma_separated_ids_to_request = [",".join(players_to_request_at_once) for
                                      players_to_request_at_once in split_players_list]  # list of lists
    urls_to_request = [base_url+comma_separated_id_group for comma_separated_id_group in comma_separated_ids_to_request]

    players_with_names = {}
    for url in urls_to_request:
        json_returned = json.loads(request.urlopen(url).read())
        players_json = json_returned["response"]["players"]  # a list of json objects with info for each player
        players_with_names_from_request = {}
        for player_json in players_json:
            players_with_names_from_request[player_json["personaname"]] = player_json["steamid"]
        players_with_names.update(players_with_names_from_request)
    # Sort dict alphabetically by keys, uppercase because otherwise lowercase letters go after Z, oddly enough
    players_with_names = {player: key for (player, key) in sorted(players_with_names.items(),
                                                                  key=lambda x: x[0].upper())}
    return players_with_names


# testList = ["76561198046824307", "76561198121061692", "76561198447026293"]
# test = lookup_players_by_id(testList)
