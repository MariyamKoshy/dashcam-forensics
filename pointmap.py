#This python file generates a kml file designated by periodic placemarks that can be used to visualise the data in an external API.
from math import radians, cos, sin, asin, sqrt
import os
import sys
import re
import time
from datetime import datetime, timedelta

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

def writePlace(count,time,namestr,lon,lat,zero):
    PlacemarkString = '''       <Placemark>
        <styleUrl>#icon-{0}</styleUrl>
        <name>Journey at {1}</name>
        <description>{2}</description>
        <Point>
	      <coordinates>{3},{4},{5}</coordinates>
    	</Point>
    	</Placemark>\n'''.format(count,time,namestr,lon,lat,zero)
    return PlacemarkString

def writeHeadString():
    HeadString='''<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<kml xmlns=\"http://earth.google.com/kml/2.2\">
    <Document>
    <name>Dashcam Investigation Timeline Map</name>\n'''
    return HeadString

def writeColorString(colors, count):
    ColorString = '''       <Style id="icon-''' + str(count) + '''-normal">
	      <IconStyle>
	        <color>#''' + colors[count] + '''</color>
	        <scale>1</scale>
	        <Icon>
	          <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>
	        </Icon>
	        <hotSpot x="32" xunits="pixels" y="64" yunits="insetPixels"/>
	      </IconStyle>
	      <LabelStyle>
	        <scale>0</scale>
	      </LabelStyle>
	    </Style>
	    <Style id="icon-''' + str(count) + '''-highlight">
	      <IconStyle>
	        <color>#''' + colors[count] + '''</color>
	        <scale>1</scale>
	        <Icon>
	          <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>
	        </Icon>
	        <hotSpot x="32" xunits="pixels" y="64" yunits="insetPixels"/>
	      </IconStyle>
	      <LabelStyle>
	        <scale>1</scale>
	      </LabelStyle>
	    </Style>
	    <StyleMap id="icon-''' + str(count) + '''">
	      <Pair>
	        <key>normal</key>
	        <styleUrl>#icon-''' + str(count) + '''-normal</styleUrl>
	      </Pair>
	      <Pair>
	        <key>highlight</key>
	        <styleUrl>#icon-''' + str(count) + '''-highlight</styleUrl>
	      </Pair>
    	</StyleMap>\n'''
    return ColorString

def generatepointKML():
    if len(sys.argv)<1:
        print >> sys.stderr, __doc__

    else:
        placestring = ''
        HeadStr = ''
        FList = []
        colors = ['761a49','ff4499', 'ffff00', 'ff0000', 'ff4500', 'c71585', '1a7667', 'adff2f', 'f6a600', '008000', '00ff7f', '008080', '66cdaa', '0000cd', '6a5acd', '800080', 'ff00ff', '8b4513', '000000', '00008b'] 
        color_count = 0
        iter = 0 
        EndString = """</Document>
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
                            currdatetime = datetime.strptime(V.rstrip(), "%Y:%m:%d %H:%M:%S%z")
                            cnt += 1
                        elif "Latitude" in K:
                            lat = decimalat(V)
                            cnt += 1
                        elif "Longitude" in K:
                            lon = decimalat(V)
                            cnt += 1
                        elif "GPS Speed" == K.rstrip():
                            speedkmph = V + ' kph'
                            speedmph = str(round(0.621371 * float(V), 4)) + ' mph'
                            speedstr = speedkmph + '/' + speedmph
                            cnt += 1
                        if cnt == 4:
                            TimeFmt = "%H:%M"
                            DateFmt = "%d-%m-%Y"
                            name_str = 'Date : ' + str(time.strftime(DateFmt,timetuple)) + '\n' + 'Time : ' + str(time.strftime("%H:%M:%S",timetuple)) + '\n' + 'Speed : ' + speedstr
                            if iter == 0:
                                prevdate = currdate
                                prevdatetime = currdatetime
                                HeadStr = writeHeadString()
                                HeadStr += writeColorString(colors, color_count)
                                iter += 1
                            if prevdate == currdate:
                                if prevdatetime is currdatetime:
                                    placestring += writePlace(color_count,str(time.strftime(TimeFmt,timetuple)),name_str,lon,lat,'0')   
                                if prevdatetime is not currdatetime:
                                    diff = currdatetime - prevdatetime
                                    if diff >= timedelta(minutes=3):
                                        placestring += writePlace(color_count,str(time.strftime(TimeFmt,timetuple)),name_str,lon,lat,'0')
                                        prevdatetime = currdatetime
                            elif prevdate != currdate:
                                if color_count < 20:
                                    color_count += 1
                                else:
                                    color_count = 0
                                placestring += writeColorString(colors, color_count)
                                placestring += writePlace(color_count,str(time.strftime(TimeFmt,timetuple)),name_str,lon,lat,'0')
                                prevdate = currdate
                            cnt = 0

        with open('pointoutput.kml', 'w') as outfile:
            outfile.write(HeadStr + '\n' + placestring + EndString)