import bisect
import json
import random
import seaborn
import numpy
import scipy
from matplotlib import pyplot

def parse_time(t):
    h, m, s = map(int, t.split(':'))
    return h*60*60 + m*60 + s

sched_trips = {}
for i, line in enumerate(open('stop_times.txt')):
    line = line.strip().split(',')
    if i > 0:
        trip_id, arr, dep, stop_id  = line[:4]
        trip_id_short = trip_id.split('_', 1)[1]
        key = (stop_id, trip_id_short)
        arr = parse_time(arr)
        sched_trips.setdefault(key, {})[trip_id] = arr

real_trips = {}
for n_lines, line in enumerate(open('log.jsons')):
    for vehicle in json.loads(line.strip()):
        if vehicle.get('current_status') != 1: # STOPPED_AT
            continue
        try:
            line = vehicle['trip']['route_id'].rstrip('X') # fold express into normal
            if line not in ['1', '2', '3', '4', '5', '6', 'GS', 'L', 'SI']:
                print 'weird line', line
                continue
            if 'stop_id' in vehicle:
                stop_id = vehicle['stop_id']
            else:
                # L and SI stop at every station, need to use 
                stop_id = '%d%s' % (vehicle['current_stop_sequence'], vehicle['trip']['trip_id'][-1])
            key = (stop_id, line)
            timestamp = vehicle['timestamp']
            real_trips.setdefault(key, []).append((timestamp, vehicle['trip']['trip_id']))
        except:
            print 'weird vehicle', vehicle
            continue
    if n_lines == 1000:
        break

xs = []
ys = []

for key, stops in real_trips.iteritems():
    stop_id, line = key

    stops.sort()

    # Sample random points in time and tie 
    lo, _ = stops[0]
    hi, _ = stops[-1]
    for i in xrange(10):
        t = lo + random.random() * (hi - lo)
        j = bisect.bisect(stops, (t, None))
        t0, id0 = stops[j-1]
        t1, id1 = stops[j]
        print sched_trips.get((stop_id, id0)), sched_trips.get((stop_id, id1))
        
