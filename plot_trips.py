import datetime
import json
import matplotlib.pyplot as plt
import pytz

# nyc_tz = pytz.timezone('US/Eastern')

stops = {}
for line in open('stops.txt'):
    stop_id, _, stop = line.strip().split(',')[:3]
    if stop_id[-1] == 'N':
        try:
            stops[int(stop_id[:-1])] = stop
        except:
            print 'could not parse', stop_id, stop

print stops

def datetime2timestamp(d):
    return (d - datetime.datetime(1970, 1, 1)).total_seconds()


def read_data(date_a, date_b, margin):
    date_a, date_b = (datetime2timestamp(d) for d in(date_a, date_b))
    trips = {}
    for line in open('log.jsons'):
        for vehicle in json.loads(line.strip()):
            if vehicle.get('current_status') != 1: # STOPPED_AT
                continue
        
            if vehicle['trip']['route_id'][:1] != '1':
                continue

            t = vehicle['timestamp']
                        
            if t > date_b + margin:
                return trips

            if t < date_a - margin:
                continue
        
            stop = vehicle['stop_id']
            trip = (vehicle['trip']['start_date'], vehicle['trip']['trip_id'])
            trips.setdefault(trip, {})[t] = stop

date_a, date_b = [datetime.datetime(2016, 3, 3, 14), datetime.datetime(2016, 3, 3, 20)]
margin = 0 # 3600 * 3
plt.figure(figsize=(24, 6))
unique_ys = set()
for trip, seq in read_data(date_a, date_b, margin).iteritems():
    if len(seq) < 10:
        continue
    seq = sorted(seq.items())
    ts = [datetime.datetime.utcfromtimestamp(t) for t, _ in seq]
    ys = [int(s[:-1]) for _, s in seq]
    unique_ys.update(ys)
    plt.plot(ts, ys, '#EE352E', lw=2.0) #, tz=nyc_tz)

plt.yticks(sorted(unique_ys), [stops[y] for y in sorted(unique_ys)])
plt.xlim([date_a, date_b])
plt.tight_layout()    
plt.savefig('trips.png')

        
