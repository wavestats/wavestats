def frames_to_timecode(frames, seconds_only=False):  # https://gist.github.com/schiffty/c838db504b9a1a7c23a30c366e8005e8
    if frames in [b"inf", float("inf")]:
        return b"inf"
    try:
        frames = float(frames)
    except OverflowError:
        print("oh this actually happened")
        print(frames)
        return b"inf"
    m = int(frames / 3600)
    s = (frames % 3600)/60
    if seconds_only:
        return b"%02g" % s
    return b"%02d:%02g" % (m, s)
