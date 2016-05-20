import bisect
import datetime
import json
import random
import seaborn
import numpy
import pandas
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
        if 'WKD' not in trip_id:
            continue
        line = trip_id.split('_')[2].split('.')[0]
        key = (stop_id, line)
        arr = parse_time(arr)
        sched_trips.setdefault(key, []).append(arr)

for key, stops in sched_trips.iteritems():
    stops.sort()

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
            t = datetime.datetime.utcfromtimestamp(vehicle['timestamp'])
            if t.weekday() < 5:
                real_trips.setdefault(key, set()).add(timestamp)
        except:
            print 'weird vehicle', vehicle
            continue
    if n_lines % 1000 == 0:
        print n_lines, '...'

xs = []
ys = []

MAX = 1800

ys_by_x = [[] for x in xrange(MAX/60)]
print ys_by_x

for key, stops in real_trips.iteritems():
    stop_id, line = key

    stops = sorted(stops)
    if len(stops) < 5:
        print key, 'not enough stops'
        continue # stupid
    if key not in sched_trips:
        print key, 'has no schedule'
        continue

    # Sample random points in time and tie 
    lo = stops[0]
    hi = stops[-1]
    for i in xrange(len(stops)): # pretty arbitrary number of samples
        t = lo + random.random() * (hi - lo)
        j = bisect.bisect(stops, t)
        t1 = stops[j]
        real_wait_time = t1 - t
        # transform t to day offset
        u = (t + (19 * 60 * 60)) % (24 * 60 * 60)
        j = bisect.bisect(sched_trips[key], u)
        if j < len(sched_trips[key]):
            u1 = sched_trips[key][j]
        else:
            u1 = 24 * 60 * 60 + sched_trips[key][0]
        sched_wait_time = u1 - u

        if max(sched_wait_time, real_wait_time) < MAX:
            xs.append(sched_wait_time / 60.)
            ys.append(real_wait_time / 60.)

            print int(sched_wait_time/60.0), len(ys_by_x)
            ys_by_x[int(sched_wait_time / 60.0)].append(real_wait_time / 60.)

seaborn.jointplot(numpy.array(xs), numpy.array(ys), kind='hex')
# pyplot.xlim([0, 1800])
# pyplot.ylim([0, 1800])
pyplot.show()

pyplot.clf()
percs = [50, 60, 70, 80, 90]
results = [[] for p in percs]
for x, ys in enumerate(ys_by_x):
    print x, len(ys)
    ps = numpy.percentile(ys, percs)
    for i, y in enumerate(ps):
        results[i].append(y)

for i, ys in enumerate(results):
    pyplot.plot(range(len(ys)), ys, label='%d percentile' % percs[i])
pyplot.show()
