import json
import random
import bisect
import numpy
from matplotlib import pyplot
import datetime

def parse_time(t):
    h, m, s = map(int, t.split(':'))
    return h*60*60 + m*60 + s

# Need to map stop sequence to stop id for L and SI
#seq2stop = {}
#for i, line in enumerate(open('stop_times.txt')):
#    line = line.strip().split(',')
#    if i > 0:
#        trip_id, arr, dep, stop_id, stop_sequence  = line[:5]
#        trip_id_short = trip_id.split('_', 1)[1][:11]
#
#        if 'WKD' not in trip_id:
#            continue
#        if 'L' not in trip_id_short and 'SI' not in trip_id_short:
#            continue
#
#        k = (trip_id_short, stop_sequence)
#        if k in seq2stop and seq2stop[k] != stop_id:
#            print k, stop_id, seq2stop[k]
#            raise
#        seq2stop[k] = stop_id

stops = {}
for i, line in enumerate(open('stops.txt')):
    line = line.strip().split(',')
    if i > 0:
        stop_id, _, stop_name = line[:3]
        if stop_id in stops and stops[stop_id] != stop_name:
            raise
        stops[stop_id] = stop_name

print stops

stations = {}
for n_lines, line in enumerate(open('log.jsons')):
    if n_lines % 1000 == 0:
        print n_lines, '...'
    try:
        vehicles = json.loads(line.strip())
    except:
        print 'could not parse', line
        continue
    for vehicle in vehicles:
        if vehicle.get('current_status') != 1: # STOPPED_AT
            continue
        try:
            line = vehicle['trip']['route_id'].rstrip('X') # fold express into normal
            if 'stop_id' not in vehicle:
                continue
            timestamp = vehicle['timestamp']
            stations.setdefault((vehicle['stop_id'], line), set()).add(timestamp)
        except:
            raise
            print 'weird vehicle', vehicle
            continue

delays = {}

for key, timestamps in stations.iteritems():
    stop_id, line = key
    timestamps = sorted(list(timestamps))
    if len(timestamps) < 100:
        continue
    lo, hi = timestamps[0], timestamps[-1]
    for i in xrange(1000):
        t = lo + random.random() * (hi - lo)
        j = bisect.bisect_left(timestamps, t)
        t0, t1 = timestamps[j-1], timestamps[j]
        if t1 - t0 < 4 * 3600:
            delays.setdefault(key, []).append(t1 - t)

for k in sorted(delays.keys(), key=lambda k: numpy.median(delays[k])):
    stop_id, line = k
    print stop_id, line, len(stations[k]), numpy.median(delays[k]), stops[stop_id]

