#Here GPS metadata from the videos are extracted to generate a JSON file.
from math import radians, cos, sin, asin, sqrt
import os
import sys
import re
import time
import json 
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="Nominatim")

def decimalat(DegString):
    # This function requires that the re module is loaded
    # Take a string in the format "34 56.78 N" and return decimal degrees
    SearchStr=r''' *(\d+) deg (\d+)' ([\d\.]+)" (\w)'''
    Result = re.search(SearchStr, DegString)

    # Get the (captured) character groups from the search
    Degrees = float(Result.group(1))
    Minutes = float(Result.group(2))
    Seconds = float(Result.group(3))
    Compass = Result.group(4).upper() # make sure it is capital too

    # Calculate the decimal degrees
    DecimalDegree = Degrees + Minutes/60 + Seconds/(60*60)
    if Compass == 'S' or Compass == 'W':
        DecimalDegree = -DecimalDegree  
    return DecimalDegree 

def writePlace(place,date,time,datetimestr):
    PlacemarkString = "{0},{1},{2},{3}\n".format(place,date,time,datetimestr)
    return PlacemarkString

def findLocation(lon,lat,timetuple,DateFmt,speed):
    TimeFmt = "%H:%M:%S"
    locstr = str(lat) + ',' + str(lon)
    location = geolocator.reverse(locstr)
    address = str(location.address)
    datestr = str(time.strftime(DateFmt,timetuple))
    timestr = str(time.strftime(TimeFmt,timetuple))
    addr = address.replace(",","")
    return 'Date: ' + datestr + ', Time: ' + timestr + ', Speed: ' + speed + ', Address: ' + addr   

def buildInfo():    
    placestring = ''
    FList = []
    iter = 1
    for filename in os.listdir():
        if filename.endswith(".MOV") or filename.endswith(".MP4") or filename.endswith(".JPG") or filename.endswith(".3gp"):
            FList.append(filename)
            continue
        else:
            pass

    for F in FList:
        ExifData=os.popen('exiftool -a -gps* -ee "'+ F).read()
        if "Longitude" in ExifData:
            ExifData.rstrip()
            Fields = ExifData.split("\n")
            cnt = 0
            #lon = 0
            for Items in Fields:
                if len(Items)> 20:
                    K,V = Items.split(" : ")
                    if "Latitude" in K:
                        lat = decimalat(V)
                        cnt += 1
                    elif "Longitude" in K:
                        lon = decimalat(V)
                        cnt += 1
                    elif "Date" in K:
                        timetuple = time.strptime(V.rstrip(),"%Y:%m:%d %H:%M:%S%z")  # time format
                        currdatetime = datetime.strptime(V.rstrip(), "%Y:%m:%d %H:%M:%S%z")
                        cnt += 1
                    elif "GPS Speed" == K.rstrip():
                        speedkmph = V + ' kph'
                        speedmph = str(round(0.621371 * float(V), 4)) + ' mph'
                        speedstr = speedkmph + '/' + speedmph
                        cnt += 1
                    if cnt == 4:
                        TimeFmt = "%H:%M"
                        DateFmt = "%d-%m-%Y"
                        DateTimeFmt = "%Y-%m-%dT%H:%M:%S"
                        if iter == 1:
                            prevdatetime = currdatetime
                            iter = 0
                        if prevdatetime is currdatetime:
                            placestring += writePlace('{"Information" : ' + '"' + str(findLocation(lon,lat,timetuple,DateFmt,speedstr)) + '"',' "Date" : ' + '"' + str(time.strftime(DateFmt,timetuple)) + '"',' "Time" : ' + '"Journey at ' + str(time.strftime(TimeFmt,timetuple)) + '"',' "Date-Time" : ' + '"' + str(time.strftime(DateTimeFmt,timetuple)) + '"' + '}')
                        if prevdatetime is not currdatetime:
                            diff = currdatetime - prevdatetime
                            if diff >= timedelta(minutes=3):
                                placestring += writePlace('{"Information" : ' + '"' + str(findLocation(lon,lat,timetuple,DateFmt,speedstr)) + '"',' "Date" : ' + '"' + str(time.strftime(DateFmt,timetuple)) + '"',' "Time" : ' + '"Journey at ' + str(time.strftime(TimeFmt,timetuple)) + '"',' "Date-Time" : ' + '"' + str(time.strftime(DateTimeFmt,timetuple)) + '"' + '}')
                                prevdatetime = currdatetime
                        cnt = 0
    return placestring

#converting text into JSON
def getJSONData():
    with open('output.txt', 'w') as outfile:
        outfile.write(buildInfo())
    list = []
    with open("output.txt", "r") as a_file:
        for line in a_file:
            outdictionary = json.loads(line)
            list.append(outdictionary)

    json_object = json.dumps(list, indent = 4)

    with open('output.json', 'w') as outfile:
        outfile.write(json_object)