import json
import datetime
import seaborn
import numpy
import math
import pandas
from matplotlib import pyplot

stations = {}
for line in open('log.jsons'):
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
next_subway = []
next_subway_by_time_of_day = [[] for x in xrange(24 * 60)]
next_subway_by_line = []
for key, values in stations.iteritems():
    values = sorted(values)
    print key, len(values)
    last_value = None
    for i in xrange(1, len(values)):
        last_value, value = values[i-1], values[i]
        deltas.append(value - last_value)
        for t in xrange(next_whole_minute(last_value), value, 60):
            x = (t // 60 + 19 * 60) % (24 * 60) # 19 from UTC offset
            next_subway_by_time_of_day[x].append(value - t)
            next_subway.append(value - t)
            next_subway_by_line.append({'x': line, 'y': value - t})

# Plot distributions of deltas
for data, fn, title, color in [(deltas, 'time_between_arrivals.png', 'Distribution of delays between subway arrivals', 'blue'),
                               (next_subway, 'time_to_next_arrival.png', 'Distribution of time until the next subway arrival', 'red')]:
    print 'got', len(data), 'points'
    lm = seaborn.distplot([d for d in data if d < 7200], bins=60, color=color)
    pyplot.xlim([0, 3600])
    pyplot.title(title)
    pyplot.xlabel('Time (s)')
    pyplot.ylabel('Probability distribution')
    pyplot.savefig(fn)

# Plot deltas by line
seaborn.boxplot(x='x', y='y', data=pandas.DataFrame(deltas_by_line),
                order=['1', '2', '3', '4', '5', '6', 'GS', 'L', 'SI'],
                palette=['#EE352E']*3 + ['#00933C']*3 + ['#808183', '#A7A9AC', '#000000'])
pyplot.ylim([0, 1800])
pyplot.title('Time until the next subway')
pyplot.xlabel('Line')
pyplot.ylabel('Time (s)')
pyplot.savefig('time_to_arrival_by_line.png')

# Plot distribution of delays by time of day
percs = [50, 60, 70, 80, 90]
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
