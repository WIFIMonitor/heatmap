from influxdb import InfluxDBClient
import plotly.express as px
import ffmpeg
import os


client = InfluxDBClient("XXX.XXX.XXX.XXX", XXX, "XXXX", "XXXXXXX", "XXXXXXXX")
# get the last timestamp value of the database
lasttimestamp= client.query("select last(clientsCount), time from clientsCount").raw['series'][0]['values'][0][0]
prev_ts = lasttimestamp
# load ap cooordinates into memory, so that we dont 
# have to read the excel file every time someone
# wants to check the heatmap
def load_ap_coords():
    coords = {}
    f = open("fileCoords.txt","r")
    
    for line in f:
        info = line.split(",")
        dic = { 
        "lat" : info[1],
        "lon" : info[2].strip('\n'),
        "piso" : info[3] if info[3]!="None\n" else "Não Definido",
        "people" : 0
        }
        coords[info[0]] = dic
    
    f.close()
    return coords

def get_dictionary(coordinates,timesub):
    # since we get values every 15 minutes, we need to now how many 15 minute measures we want
    sub1 = str(15*timesub)
    sub2 = str(15*(timesub-1))
    # query values between last measurement, minus 15 minutes
    sq = "select id,clientsCount from clientsCount where time <=\'" + str(prev_ts) + "\'-"+sub2+"m and time > \'" + str(prev_ts) + "\'-"+sub1+"m and clientsCount > 0" 
    # get the last 15m values, from the last value in DB, and not from now(), because CISCO PRIME can stop sending values
    try:
        people_count = client.query(sq).raw['series'][0]["values"]
    except:
        return

    dataset = []
    for line in people_count:
        if line[1] in coordinates:
            coordinates[line[1]]["people"]=line[2]
            dataset.append(coordinates[line[1]])
        else:
            continue
    
    return dataset

def createVideo():
    if os.path.exists("timelapse.avi"):
        os.remove("timelapse.avi")
    
    (
    ffmpeg
    .input('output/*.jpeg', pattern_type='glob', framerate=5)
    .output('timelapse.avi')
    .run()
    )

    print("Video Created! ")

coords = load_ap_coords()
# Generate 10 timelaspes. In the future it will be decided by the user input
for x in range(1,50):
    try:
        df = get_dictionary(coords,x)
        fig = px.density_mapbox(df, lat='lat', lon='lon', z='people', radius=10,
                            center=dict(lat=40.63041451444991, lon=-8.65803098047244),
                            zoom=15,
                            mapbox_style="stamen-terrain",
                            width=550,
                            height=1100,
                            color_continuous_scale= [
                [0.0, "green"],
                [0.3, "green"],
                [0.5, "yellow"],
                [0.7, "yellow"],
                [0.9, "red"],
                [1.0, "red"]],
                            title= str(prev_ts) + "- " + str((x*15)) + "m",
                            range_color=(0,30), #max and min values for heatmap
                            ) 
        fs = "output/file" + f"{x:03d}" + ".jpeg"
        fig.write_image(fs,scale=0.5)
    except Exception as e:
        print(e)
        continue
    
createVideo()
