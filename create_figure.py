import matplotlib.pyplot as plt
import io
import base64


def create_figure(ticks, values, labels):
    plt.figure(figsize=(17, 8))
    plt.bar(ticks, values)
    plt.xlabel("Level (Format: [World Number]-[Level Number])")
    plt.ylabel("Frames to Save")
    plt.xticks(range(min(ticks), max(ticks)+1, 1), labels=labels)  # set tick marks to be 1 apart and label ticks
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format="png")
    bytes_image.seek(0)
    # get value returns a string which we can then encode as base 64, which lets us embed it in html
    return base64.b64encode(bytes_image.getvalue()).decode()
