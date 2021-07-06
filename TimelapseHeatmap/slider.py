from influxdb import InfluxDBClient
from datetime import datetime,time,timedelta
import plotly.express as px
import timeit

client = InfluxDBClient("XXX.XXX.XXX.XXX", XXX, "XXXX", "XXXXXXX", "XXXXXXXX")
# get the last timestamp value of the database
def get_last_ts():
    # get the last timestamp value of the database
    return client.query("select last(clientsCount) from clientsCount").raw['series'][0]['values'][0][0]

def load_ap_coords():
    coords = {}
    f = open("../fileCoords.txt","r")

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

coords = load_ap_coords()

def get_timelapse_dictionary(starttime,measure):
    # query values between last measurement, minus 15 minutes
    sq = "select id,clientsCount from clientsCount where time >=\'"+starttime
    # get the last 15m values, from the last value in DB, and not from now(), because CISCO PRIME can stop sending values
    try:
        people_count = client.query(sq).raw['series'][0]["values"]
    except Exception as e:
        print(e)
        return []
    
    # create dataset of the measures between the two start and end times
    dataset = []
    for line in people_count:
        # only add to the timelapse points that have people conected, to not overload the array
        if line[2] != 0:
            if line[1] in coords:
                dic = { "lat": coords[line[1]]["lat"],
                        "lon":coords[line[1]]["lon"],
                        "people":line[2],
                        "measure":measure,
                        }
                dataset.append(dic)
            else:
                continue

    return dataset
    
def generateTimelapse(start,days):
    #create a dataset with the measures for the day
    dataset = []
    start_time = datetime.strptime(str(start), "%Y-%m-%d").isoformat('T')
    # add hours,minutes and seconds precision to above date
    time_measure= datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%S') 
    # Generate timelaspes X timelapses, where X is 96 * days, because, theres 96 measures in each day
    for x in range(0,(96*days),4):
        try:
            # since we get values every 15 minutes, we need to now how many 15 minute measures we want
            offset = str(15*x)
            offset2 = str(15*(x+1))
            query_time = start_time + "Z\' +"+offset+"m and time <= \'" + start_time + "Z\' + "+offset2+"m"
            # add 15 minutes to each query, for better visualization of the slider
            measure_time = time_measure + timedelta(minutes=(float(offset2)))
            slider_step = str(measure_time)[11:16] # only get the Hours:Minutes part of the string
            # extend yeilds better performance, rather than apppending an array of 776 items
            dataset.extend(get_timelapse_dictionary(query_time,slider_step))
        except Exception as e:
            print(e)
            continue
    # create the timelapse, where the slider represents the time of the measure of people connected
    fig = px.density_mapbox(dataset, lat='lat', lon='lon', z='people', radius=10,animation_frame='measure',
            center=dict(lat=40.63193066543083, lon=-8.658186691344712),
            zoom=15,
            mapbox_style="stamen-terrain",
            width=900,
            height=700,
            color_continuous_scale= [   # color scale for the heatmap
                    [0.0, "green"],
                    [0.3, "green"],
                    [0.5, "yellow"],
                    [0.7, "yellow"],
                    [0.9, "red"],
                    [1.0, "red"]],
            title= "Timelapse de: " + start_time[0:10], 
            range_color=(0,30), #max and min values for heatmap
            )
    return fig.write_html("sliderteste.html")
    
start = timeit.default_timer()
generateTimelapse("2021-06-04",1)
end = timeit.default_timer()
print("Time elapsed: ",end-start)
