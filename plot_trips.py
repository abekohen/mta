import datetime
import json
import matplotlib.pyplot as plt
import pytz

# nyc_tz = pytz.timezone('US/Eastern')

def read_data(date_a, date_b, margin):
    trips = {}
    for line in open('log.jsons'):
        for vehicle in json.loads(line.strip()):
            if vehicle.get('current_status') != 1: # STOPPED_AT
                continue
        
            if vehicle['trip']['route_id'][:1] != '1':
                continue

            t = vehicle['timestamp']
                        
            if t > date_b:
                return trips

            if t < date_a-margin or t > date_b+margin:
                continue
        
            stop = vehicle['stop_id']
            trip = (vehicle['trip']['start_date'], vehicle['trip']['trip_id'])
            trips.setdefault(trip, {})[t] = stop

date_a, date_b = (int(dt.strftime('%s')) for dt in [datetime.datetime(2016, 3, 3, 14), datetime.datetime(2016, 3, 3, 20)])
margin = 3600 * 3
plt.figure(figsize=(24, 6))
for trip, seq in read_data(date_a, date_b, margin).iteritems():
    if len(seq) < 10:
        continue
    seq = sorted(seq.items())
    ts = [datetime.datetime.utcfromtimestamp(t) for t, _ in seq]
    ys = [int(s[:-1]) for _, s in seq]
    plt.plot_date(ts, ys, '#00933C') #, tz=nyc_tz)
    plt.xlim([date_a, date_b])

plt.tight_layout()    
plt.savefig('trips.png')

        
