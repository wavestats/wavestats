from flask import Flask, render_template, redirect, url_for, request
from form import SteamKeyForm
from get_scores import get_scores_from_steamkey
from list_players import get_players_finished_game
from lookup_player_by_id import lookup_players_by_id
from create_figure import create_figure
from frames_to_timecode import frames_to_timecode
from statistics import mean

app = Flask(__name__)

app.config["SECRET_KEY"] = "test"


@app.route("/", methods=["GET", "POST"])
def home():
    form = SteamKeyForm()
    if form.validate_on_submit():  # basically, if our form was submitted and was not invalid (which it can't be rn)
        return redirect(url_for("result", steamkey=form.data["steamKey"].encode(),
                                analysis=form.data["analysisType"].encode()))
    players_finished_game = get_players_finished_game()
    players_with_names = lookup_players_by_id(players_finished_game)
    return render_template("form_template.html", form=form, players_with_names=players_with_names)


@app.route("/leaderboard")  # For overall time comparison
def leaderboard():
    analysis_type = request.args.get("analysis").encode()
    players_finished_game = get_players_finished_game()
    players_with_names = lookup_players_by_id(players_finished_game)
    names = [name for name in players_with_names.keys()]
    scores_by_player = [get_scores_from_steamkey(steamkey.encode(), analysis_type) for
                        steamkey in players_with_names.values()]  # list of lists of dicts (list of dicts 4each player)

    summed_scores = []  # becomes a list with 1 summed score for each player
    for player_list in scores_by_player:
        player_times = []
        for level in player_list:
            level_time = level["user_score"]
            player_times.append(float(level_time))
        summed_scores.append(sum(player_times))

    sobs_by_name = {player: [time_sum, frames_to_timecode(time_sum)] for
                    (player, time_sum) in zip(names, summed_scores)}

    sorted_sobs_by_name = {player: time_sums for (player, time_sums) in  # sort by frame count
                           sorted(sobs_by_name.items(), key=lambda x: x[1][0])}

    lines_to_print = [f"Rank {i}: {kv_pair[0]} -- Time: {kv_pair[1][1].decode()} s ({kv_pair[1][0]} frames)" for
                      i, kv_pair in enumerate(sorted_sobs_by_name.items(), 1)]

    return render_template("leaderboard_template.html", lines_to_print=lines_to_print)


@app.route("/result")
def result():
    steamkey = request.args.get("steamkey").encode()
    analysis_type = request.args.get("analysis").encode()
    if analysis_type == b"dark":
        search_strings = [f"World {world} Level {level}" for world in range(1, 6) for level in range(1, 7)]
    else:
        search_strings = [f"World {world} Level {level}" for world in range(1, 7) for level in range(1, 7)]
    differences = []
    lines_to_print = []
    scores = get_scores_from_steamkey(steamkey, analysis_type)  # maybe should be called lvl_results?
    # must convert to float before converting to int b/c they are float strings. Since we cannot convert float(b"inf")
    # to an int, we can just return float(b"inf") in that case (since either way it just displays as inf)
    user_scores = [int(float(score_dict["user_score"].decode())) if score_dict["user_score"] != b"inf" else
                   float(score_dict["user_score"]) for score_dict in scores]

    ranks = [int(float(score_dict["rank"].decode())) if score_dict["rank"] != b"inf" else
             float(score_dict["rank"]) for score_dict in scores]

    mean_rank = mean(ranks)
    best_scores = [int(float(score_dict["best_score"].decode())) for score_dict in scores]
    user_seconds = [float(score_dict["user_seconds"].decode()) for score_dict in scores]
    best_seconds = [float(score_dict["best_seconds"].decode()) for score_dict in scores]
    user_sob_frames = sum(user_scores)
    user_sob_ms = frames_to_timecode(user_sob_frames).decode()
    world_sob_frames = sum(best_scores)
    world_sob_ms = frames_to_timecode(world_sob_frames).decode()
    total_difference_frames = user_sob_frames - world_sob_frames
    total_difference_ms = frames_to_timecode(total_difference_frames).decode()

    for search_string, user_score, best_score, user_second, best_second, rank in\
            zip(search_strings, user_scores, best_scores, user_seconds, best_seconds, ranks):
        difference = user_score - best_score
        if difference != float("inf"):
            differences.append(difference)
        lines_to_print.append(f"{search_string} -- User time: {user_second} s ({user_score} frames) | Best time: "
                              f"{best_second} s ({best_score} frames) (difference {difference} frames) || Rank: {rank}")
    # level_ids represents indexes in search_strings where the user time is not inf, so we can use it to get levels
    # from search_strings that we want to include in the chart labels (see assignment of level_labels)
    level_ids = [i for i, score in enumerate(user_scores) if score != float("inf")]
    level_ticks = [i for i in range(len(level_ids))]  # Determines x-axis tick spacing, obv. all should be 1 space apart
    level_labels = [search_strings[i][6] + "-" + search_strings[i][14] for i in level_ids]  # eg. "1-1"
    plot_string = create_figure(level_ticks, differences, level_labels)
    return render_template("result_template.html", lines_to_print=lines_to_print, plot_string=plot_string,
                           world_sob_frames=world_sob_frames, world_sob_ms=world_sob_ms,
                           user_sob_frames=user_sob_frames, user_sob_ms=user_sob_ms, mean_rank=mean_rank,
                           total_difference_ms=total_difference_ms, total_difference_frames=total_difference_frames)


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
