#The main executable python file.Equivalent to main.py.The JSON files are used to generate stemplots for the timeline.
#The timelines are generated for each date.
import os
import json
import time
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime
import mplcursors
from matplotlib.font_manager import FontProperties
from map import generateKML
from splitjson import splitJSONdata
from pointmap import generatepointKML

generateKML()
generatepointKML()
splitJSONdata()

Flist = []
for filename in os.listdir():
    if filename.endswith(".json"):
        Flist.append(filename)
        continue
    else:
        pass

for file in Flist:
    names = []
    times = []
    datetimes = []
    datestr = ''
    try:
        with open(file, "r") as f:
            data = json.load(f)

        for item in data:
            times.append(item['Time'])
            names.append(item['Information'].replace(", ","\n"))
            datetimes.append(item['Date-Time'])

        # Convert date strings (e.g. 2014-10-18) to datetime
        datetimes = [datetime.strptime(d, "%Y-%m-%dT%H:%M:%S") for d in datetimes]

    except Exception:
        print("Error Connection")


    # Choose some nice levels
    levels = np.tile([-9, 9, -7, 7, -5, 5, -3, 3, -1, 1],int(np.ceil(len(datetimes)/10)))[:len(datetimes)]

    # Create figure and plot a stem plot with the date
    fig, ax = plt.subplots(figsize=(10, 4), constrained_layout=False)
    ax.set(title="Dashcam Investigation Timeline")

    markerline, stemline, baseline = ax.stem(datetimes, levels, linefmt="C3-", basefmt="k-", use_line_collection=True)

    plt.setp(markerline, mec="k", mfc="w", zorder=3)

    # annotate lines
    vert = np.array(['top', 'bottom'])[(levels > 0).astype(int)]
    for d, l, r, va in zip(datetimes, levels, times, vert):
        ax.annotate(r, xy=(d, l), xytext=(-3, np.sign(l)*3), textcoords="offset points", va=va, ha="center", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))

    # format xaxis with 1 day intervals
    ax.get_xaxis().set_major_locator(mdates.DayLocator(interval=1))
    ax.get_xaxis().set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="center")
    
    # Placing notes
    font = {'color': 'darkred',}
    ax.set_xlabel('PLEASE CLICK ON THE SEMICIRCLES FOR VIEWING THE DRAGGABLE ATTRIBUTE BOX',fontdict=font)

    # remove y axis and spines
    ax.get_yaxis().set_visible(False)
    for spine in ["left", "top", "right"]:
        ax.spines[spine].set_visible(False)

    ax.margins(y=0.1)

    #Placing draggable text boxes
    cursor = mplcursors.cursor(markerline)
    @cursor.connect("add")
    def _(sel):
        sel.annotation.set(text=names[sel.target.index])
        sel.annotation.get_bbox_patch().set(boxstyle='round,pad=1',fc="cyan")

    plt.show()

#removing the JSON files
for filename in os.listdir():
    if filename.endswith(".json") or filename.endswith(".txt"):
        os.remove(filename)
        continue
    else:
        pass