#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import orjson as json
import matplotlib.pyplot as plt

filepath = "dict/wikipedia_word_count/wikipedia-en-words-cumulative.json"


def plot_wikipedia_data(filepath):

    with open(filepath, "rb") as json_file:
        wiki_data = json.loads(json_file.read())

    percentiles = [0] * 10

    x = []
    y = []

    for data in wiki_data.values():

        # Generate line graph data
        x.append(data["id"])
        y.append(float(data["cumulative_percentage"]))

        percentage = float(data["cumulative_percentage"])

        # Generate percentile data
        if percentage < 0.1:
            percentiles[0] += 1
        elif percentage < 0.2:
            percentiles[1] += 1
        elif percentage < 0.3:
            percentiles[2] += 1
        elif percentage < 0.4:
            percentiles[3] += 1
        elif percentage < 0.5:
            percentiles[4] += 1
        elif percentage < 0.6:
            percentiles[5] += 1
        elif percentage < 0.7:
            percentiles[6] += 1
        elif percentage < 0.8:
            percentiles[7] += 1
        elif percentage < 0.9:
            percentiles[8] += 1
        else:
            percentiles[9] += 1

    for percentile, i in enumerate(percentiles):
        print(f"{i*10} percentile: {percentile}")

    # plot line graph with cumulative percentages
    plt.plot(x, y)
    plt.xlabel("words")
    plt.ylabel("cumulative occurrence percentage")
    plt.title("Cumulative word occurrence plot")
    plt.show()


plot_wikipedia_data(filepath)
