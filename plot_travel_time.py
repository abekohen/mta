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
        sched_trips.setdefault(trip_id_short, {}).setdefault(trip_id, {})[stop_id] = parse_time(arr)

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
                stop = vehicle['stop_id']
            else:
                # L and SI stop at every station, need to use 
                stop = '%d%s' % (vehicle['current_stop_sequence'], vehicle['trip']['trip_id'][-1])
            key = (vehicle['trip']['start_date'], vehicle['trip']['trip_id'])
            timestamp = vehicle['timestamp']
            real_trips.setdefault(key, []).append((timestamp, stop))
        except:
            print 'weird vehicle', vehicle
            continue

xs = []
ys = []

for key, stops in real_trips.iteritems():
    _, trip_id = key
    if trip_id not in sched_trips:
        print 'unknown trip', trip_id
        continue

    stops_compressed = []
    last_stop = None
    for t, stop in stops:
        if stop != last_stop:
            stops_compressed.append((t, stop))
        last_stop = stop

    for t0, stop0 in stops_compressed:
        sched = random.choice(sched_trips[trip_id].values())
        if stop0 not in sched:
            print 'weird stop for schedule', stop0
            continue
        t1, stop1 = random.choice(stops_compressed)
        if stop1 not in sched:
            print 'weird stop for schedule', stop1
            continue
        if stop0 == stop1:
            continue
        elif t0 > t1:
            t0, t1, stop0, stop1 = t1, t0, stop1, stop0
        xs.append(sched[stop1] - sched[stop0]) # timetable
        ys.append(t1 - t0) # actual

delays = (numpy.array(ys) - numpy.array(xs))
xmin, xmax = -10, 30
seaborn.distplot(delays / 60., bins=numpy.linspace(xmin, xmax, num=(xmax-xmin+1)), kde_kws={'gridsize': 2000})
mean, median, pc90 = ('%dm%02ds' % (t / 60, t % 60) for t in (numpy.mean(delays), numpy.median(delays), numpy.percentile(delays, 90)))
print mean, median, pc90
pyplot.title('Travel time delays (mean = %s, median = %s, 90th percentile = %s' % (mean, median, pc90))
pyplot.xlabel('Delay between real and scheduled (min)')
pyplot.ylabel('Probability distribution')
pyplot.xlim([xmin, xmax])
pyplot.savefig('travel_time_delay.png')

pyplot.clf()
delays_frac = numpy.array(ys) / numpy.array(xs) - 1.0
xmin, xmax = -1.0, 50
seaborn.distplot(delays_frac * 100, kde_kws={'gridsize': 2000})
mean, median, pc90 = ('%.2f%%' % x for x in (numpy.mean(delays_frac), numpy.median(delays_frac), numpy.percentile(delays_frac, 90)))
print mean, median, pc90
pyplot.title('Travel time percent delays (mean = %s, median = %s, 90th percentile = %s' % (mean, median, pc90))
pyplot.xlabel('Delay between real and scheduled (%)')
pyplot.ylabel('Probability distribution')
pyplot.xlim([xmin, xmax])
pyplot.savefig('travel_time_delay_frac.png')
