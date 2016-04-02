import json
import datetime
import seaborn
import numpy
import math
import pandas
from matplotlib import pyplot
import matplotlib

matplotlib.rcParams.update({'font.size': 48})

stations = {}
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
            key = (line, stop)
            timestamp = vehicle['timestamp'] # datetime.datetime.utcfromtimestamp(vehicle['timestamp'])
            stations.setdefault(key, set()).add(timestamp)
        except:
            print 'weird vehicle', vehicle
            continue

    #if n_lines >= 10000:
    #    break

pyplot.figure(figsize=(10, 10))

# Look at all intervals between subway arrivals
def next_whole_minute(t):
    return t+59 - (t+59)%60

deltas = []
next_subway = []
next_subway_by_time_of_day = [[] for x in xrange(24 * 60)]
next_subway_by_line_ts = []
next_subway_by_line_ls = []
next_subway_rush_hour = []
max_limit = 4 * 3600 # cap max value so that Seaborn's KDE works better
for key, values in stations.iteritems():
    line, stop = key
    values = sorted(values)
    print key, len(values)
    last_value = None
    for i in xrange(1, len(values)):
        last_value, value = values[i-1], values[i]
        if value - last_value >= max_limit:
            continue
        deltas.append(1. / 60 * (value - last_value))
        for t in xrange(next_whole_minute(last_value), value, 60):
            x = (t // 60 + 19 * 60) % (24 * 60) # 19 from UTC offset
            waiting_time = 1. / 60 * (value - t)
            next_subway_by_time_of_day[x].append(waiting_time)
            next_subway.append(waiting_time)
            next_subway_by_line_ts.append(waiting_time)
            next_subway_by_line_ls.append(line)
            if x >= 7 * 60 and x < 19 * 60:
                next_subway_rush_hour.append(waiting_time)

# Plot distributions of deltas
for data, fn, title, color in [(deltas, 'time_between_arrivals.png', 'Distribution of delays between subway arrivals', 'blue'),
                               (next_subway, 'time_to_next_arrival.png', 'Distribution of time until the next subway arrival', 'red')]:
    print 'got', len(data), 'points'
    pyplot.clf()
    lm = seaborn.distplot(data, bins=numpy.linspace(0, 60, num=61), color=color, kde_kws={'gridsize': 2000})
    pyplot.xlim([-1, 40])
    pyplot.title(title)
    pyplot.xlabel('Time (min)')
    pyplot.ylabel('Probability distribution')
    pyplot.savefig(fn)
    print 'mean', 60*numpy.mean(data), 'median', 60*numpy.median(data)

# Plot deltas by line
pyplot.clf()
seaborn.violinplot(orient='h',
                   x=next_subway_by_line_ts,
                   y=next_subway_by_line_ls,
                   order=['1', '2', '3', '4', '5', '6', 'GS', 'L', 'SI'],
                   scale='width',
                   palette=['#EE352E']*3 + ['#00933C']*3 + ['#808183', '#A7A9AC', '#555555'],
                   bw=0.03, cut=0, gridsize=2000)
pyplot.xlim([-1, 40])
pyplot.title('Time until the next subway')
pyplot.xlabel('Time (min)')
pyplot.ylabel('Line')
pyplot.savefig('time_to_arrival_by_line.png')

# Plot distribution of delays by time of day
percs = [50, 60, 70, 80, 90]
results = [[] for perc in percs]
xs = range(0, 24 * 60)
for x, next_subway_slice in enumerate(next_subway_by_time_of_day):
    print x, len(next_subway_slice), '...'
    rs = numpy.percentile(next_subway_slice, percs)
    for i, r in enumerate(rs):
        results[i].append(r)

pyplot.clf()
for i, result in enumerate(results):
    pyplot.plot([x * 1.0 / 60 for x in xs], result, label='%d percentile' % percs[i])
pyplot.ylim([0, 60])
pyplot.xlim([0, 24])
pyplot.title('How long do you have to wait given time of day')
pyplot.xlabel('Time of day (h)')
pyplot.ylabel('Time until subway arrives (min))')
pyplot.legend()
pyplot.savefig('time_to_arrival_by_time_of_day.png')

# Compute all percentiles
results = [[] for perc in percs]
offsets = numpy.arange(0, 40, 0.1)
for offset in offsets:
    print offset, '...'
    rs = numpy.percentile([d-offset for d in next_subway_rush_hour if d >= offset], percs)
    for i, r in enumerate(rs):
        results[i].append(r)

pyplot.clf()
for i, result in enumerate(results):
    pyplot.plot(offsets, result, label='%d percentile' % percs[i])
pyplot.ylim([0, 60])
pyplot.title('How long do you have to wait given that you already waited?')
pyplot.xlabel('Time you have waited for the subway (min)')
pyplot.ylabel('Additional time until subway arrives (min)')
pyplot.legend()
pyplot.savefig('time_to_arrival_percentiles.png')
