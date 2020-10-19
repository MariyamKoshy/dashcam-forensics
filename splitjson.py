#The JSON file generated in dashcam.py is split into several JSON files depending on the dates. IF videos from 5 different dates
#are present then 5 JSON files will be generated
import json
import os
from dashcam import getJSONData

getJSONData()


def writePlace(place,time,datetimestr):
    placemarkString = "{0},{1},{2}\n".format(place,time,datetimestr)
    return placemarkString

def buildJSONFile(builder_string,date):
    with open('output-' + date + '.txt', 'w') as outfile:
        outfile.write(builder_string)
    list = []
    with open('output-' + date + '.txt', "r") as a_file:
        for line in a_file:
            outdictionary = json.loads(line)
            list.append(outdictionary)

    json_object = json.dumps(list, indent = 4)

    with open('output-' + date + '.json', 'w') as outfile:
        outfile.write(json_object)

def splitJSONdata():
    count = 0
    datacount = 0
    placestring = ''
    prev_placestring = ''
    with open("output.json", "r") as f:
        data = json.load(f)
    constraint = len(data)
    for item in data:
        datacount += 1
        currdate = item['Date']
        if count == 0:
            prevdate = currdate
            count += 1
        if prevdate == currdate:
            placestring += writePlace('{"Information" : ' + '"' + item['Information'] + '"',' "Time" : ' + '"' + item['Time'] + '"',' "Date-Time" : ' + '"' + item['Date-Time'] + '"' + '}')
        elif prevdate != currdate:
            prev_placestring = placestring
            placestring = ''
            buildJSONFile(prev_placestring,prevdate)
            placestring += writePlace('{"Information" : ' + '"' + item['Information'] + '"',' "Time" : ' + '"' + item['Time'] + '"',' "Date-Time" : ' + '"' + item['Date-Time'] + '"' + '}')
            prevdate = currdate
        if datacount == constraint:
            buildJSONFile(placestring,currdate)

    os.remove("output.json")        