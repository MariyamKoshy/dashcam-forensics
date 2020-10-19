#This python file generates a kml file designated by a continuos line that can be used to visualise the data in an external API.
from math import radians, cos, sin, asin, sqrt
import os
import sys
import re
import time
from datetime import datetime

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

def writePlace(lon,lat,zero):
    PlacemarkString = "               {0},{1},{2}\n".format(lon,lat,zero)
    return PlacemarkString

def writeIntermediateString(colors, count, name):
    IntermediateString = '''           </coordinates>
        </LineString>
    </Placemark>
    <Placemark>
        <name>''' + name +'''</name>
        <Style>
            <LineStyle>
                <color>#''' + colors[count] + '''</color>
                <width>2</width>
            </LineStyle>
        </Style>
        <LineString>
            <altitudeMode>clampToGround</altitudeMode>
            <coordinates>\n'''
    return IntermediateString

def writeHeadString(name, colors):
    HeadString='''<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<kml xmlns=\"http://earth.google.com/kml/2.2\">
    <Document>
    <name>Dashcam Investigation Timeline Map</name>
    <Placemark>
    <name>''' + name +'''</name>
    <Style>
        <LineStyle>
            <color>#''' + colors[0] + '''</color>
            <width>2</width>
        </LineStyle>
    </Style>
    <LineString>
        <altitudeMode>clampToGround</altitudeMode>
        <coordinates>'''
    return HeadString

def generateKML():
    if len(sys.argv)<1:
        print >> sys.stderr, __doc__

    else:
        placestring = ''
        HeadStr = ''
        FList = []
        colors = ['761a49','ff4499', 'ffff00', 'ff0000', 'ff4500', 'c71585', '1a7667', 'adff2f', 'f6a600', '008000', '00ff7f', '008080', '66cdaa', '0000cd', '6a5acd', '800080', 'ff00ff', '8b4513', '000000', '00008b'] 
        color_count = 0
        iter = 0 
        EndString = """           </coordinates>
         </LineString>
      </Placemark>
    </Document>
</kml>"""

        for filename in os.listdir():
            if filename.endswith(".MOV") or filename.endswith(".JPG"):
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
                for Items in Fields:
                    if len(Items)> 20:
                        K,V = Items.split(" : ")
                        if "Date" in K:
                            timetuple = time.strptime(V.rstrip(),"%Y:%m:%d %H:%M:%S%z")
                            currdate = str(time.strftime("%d-%m-%Y",timetuple))
                            cnt += 1
                        elif "Latitude" in K:
                            lat = decimalat(V)
                            cnt += 1
                        elif "Longitude" in K:
                            lon = decimalat(V)
                            cnt += 1
                        if cnt == 3:
                            if iter == 0:
                                prevdate = currdate
                                HeadStr = writeHeadString(currdate, colors)
                                iter += 1
                            if prevdate == currdate:
                                placestring += writePlace(lon,lat,'0')
                            elif prevdate != currdate:
                                if color_count < 20:
                                    color_count += 1
                                else:
                                    color_count = 0
                                placestring += writeIntermediateString(colors, color_count, currdate)
                                placestring += writePlace(lon,lat,'0')
                                prevdate = currdate
                            cnt = 0

        with open('lineoutput.kml', 'w') as outfile:
            outfile.write(HeadStr + '\n' + placestring + EndString)
    