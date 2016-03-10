import json
import datetime
import seaborn
import numpy
import math
from matplotlib import pyplot

lines = {'1': '123', '2': '123', '3': '123',
         '4': '456', '5': '456', '6': '456', '5X': '456', '6X': '456',
         'GS': 'GS'}
stations = {}
for line in open('log.jsons'):
    for vehicle in json.loads(line.strip()):
        if vehicle.get('current_status') != 1: # STOPPED_AT
            continue
        try:
            line = lines[vehicle['trip']['route_id']]
            stop = vehicle['stop_id']
            key = (line, stop)
            timestamp = vehicle['timestamp'] # datetime.datetime.utcfromtimestamp(vehicle['timestamp'])
            stations.setdefault(key, set()).add(timestamp)
        except:
            print 'weird vehicle', vehicle
            continue

# Look at all intervals between subway arrivals
def next_whole_minute(t):
    return t+59 - (t+59)%60

deltas = []
next_subway_by_time_of_day = [[] for x in xrange(24 * 60)]
for key, values in stations.iteritems():
    print key, len(values)
    last_value = None
    for value in sorted(values):
        if last_value is not None:
            deltas.append(value - last_value)
            for t in xrange(next_whole_minute(last_value), value, 60):
                x = (t // 60 + 19 * 60) % (24 * 60) # 19 from UTC offset
                next_subway_by_time_of_day[x].append(value - t)
        last_value = value

# Plot distributions of deltas
print 'got', len(deltas), 'deltas'
lm = seaborn.distplot([d for d in deltas if d < 7200])
pyplot.xlim([0, 3600])
pyplot.title('Distribution of delays between subway arrivals')
pyplot.xlabel('Time (s)')
pyplot.ylabel('Probability distribution')
pyplot.savefig('time_between_arrivals.png')

# Plot distribution of delays by time of day
percs = [50, 75, 90, 95, 97, 98, 99]
results = [[] for perc in percs]
xs = range(0, 24 * 60)
for x, next_subway_deltas in enumerate(next_subway_by_time_of_day):
    print x, len(next_subway_deltas), '...'
    rs = numpy.percentile(next_subway_deltas, percs)
    for i, r in enumerate(rs):
        results[i].append(r)

pyplot.clf()
for i, result in enumerate(results):
    pyplot.plot([x * 1.0 / 60 for x in xs], result, label='%d percentile' % percs[i])
pyplot.ylim([0, 7200])
pyplot.xlim([0, 24])
pyplot.title('How long do you have to wait given time of day')
pyplot.xlabel('Time of day (h)')
pyplot.ylabel('Time until subway arrives (s)')
pyplot.legend()
pyplot.savefig('delay_by_time_of_day.png')

# Compute all percentiles
percs = [50, 75, 90, 95, 97, 98, 99]
results = [[] for perc in percs]
offsets = range(0, 20 * 60)
for offset in offsets:
    print offset, '...'
    rs = numpy.percentile([d-offset for d in deltas if d >= offset], percs)
    for i, r in enumerate(rs):
        results[i].append(r)

pyplot.clf()
for i, result in enumerate(results):
    pyplot.plot(offsets, result, label='%d percentile' % percs[i])
pyplot.ylim([0, 3600])
pyplot.title('How long do you have to wait given that you already waited?')
pyplot.xlabel('Time you have waited for the subway (s)')
pyplot.ylabel('Additional time until subway arrives (s)')
pyplot.legend()
pyplot.savefig('time_until_arrival.png')
