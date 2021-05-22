from influxdb import InfluxDBClient
import plotly.express as px
import time

client = InfluxDBClient("***REMOVED***", ***REMOVED***, "***REMOVED***", "***REMOVED***", "***REMOVED***")
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
        }
        coords[info[0]] = dic
    
    f.close()
    return coords

dataset=[]
def get_dictionary(coordinates,timesub):
    # since we get values every 15 minutes, we need to now how many 15 minute measures we want
    sub1 = str(15*timesub)
    sub2 = str(15*(timesub-1))
    # query values between last measurement, minus 15 minutes
    sq = "select id,clientsCount from clientsCount where time <=\'" + str(prev_ts) + "\'-"+sub2+"m and time > \'" + str(prev_ts) + "\'-"+sub1+"m" 
    # get the last 15m values, from the last value in DB, and not from now(), because CISCO PRIME can stop sending values
    try:
        people_count = client.query(sq).raw['series'][0]["values"]
    except:
        return
    
    for line in people_count:
        # only add to the timelapse points that have people conected, to not overload the array
        if line[2] != 0:
            if line[1] in coordinates:
                dic = {"id": line[1],
                        "lat": coords[line[1]]["lat"],
                        "lon":coords[line[1]]["lon"],
                        "piso":coords[line[1]]["piso"],
                        "people":line[2],
                        "measure":timesub,
                        }     
                dataset.append(dic)
            else:
                continue
    
coords = load_ap_coords()

# Generate 50 timelaspes. In the future it will be decided by the user input
for x in range(1,50):
    try:
        get_dictionary(coords,x)
    except Exception as e:
        print(e)
        continue

fig = px.density_mapbox(dataset, lat='lat', lon='lon', z='people', radius=10,animation_frame='measure',
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
end = time.time()
fig.write_html("slider.html")
