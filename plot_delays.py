import json
import datetime
# import seaborn
import numpy
from matplotlib import pyplot

stations = {}
for line in open('log.jsons'):
    for vehicle in json.loads(line.strip()):
        if vehicle.get('current_status') != 1: # STOPPED_AT
            continue
        try:
            key = (vehicle['trip']['route_id'].strip('X'), vehicle['stop_id'])
            timestamp = vehicle['timestamp'] # datetime.datetime.utcfromtimestamp(vehicle['timestamp'])
            stations.setdefault(key, set()).add(timestamp)
        except:
            print 'weird vehicle'
            continue

# Only look at the top 50% combinations of stations and routes
station_threshold = numpy.percentile(map(len, stations.values()), 50)
print 'threshold:', station_threshold

# Look at all intervals between subway arrivals
def next_whole_minute(t):
    return t+59 - (t+59)%60

deltas = []
next_subway_by_time_of_day = [[] for x in xrange(24 * 60)]
for key, values in stations.iteritems():
    if len(values) < station_threshold:
        continue
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
#print 'got', len(deltas), 'deltas'
#seaborn.distplot([d for d in deltas if d < 3600])
#pyplot.title('Distribution of delays between subway arrivals')
#pyplot.xlabel('Time (s)')
#pyplot.ylabel('Probability distribution')
#pyplot.savefig('time_between_arrivals.png')

# Plot distribution of delays by time of day
percs = [50, 75, 90, 95, 97, 98, 99]
results = [[] for perc in percs]
xs = range(0, 24 * 60)
for x, deltas in enumerate(next_subway_by_time_of_day):
    print x, len(deltas), '...'
    rs = numpy.percentile(deltas, percs)
    for i, r in enumerate(rs):
        results[i].append(r)

pyplot.clf()
for i, result in enumerate(results):
    pyplot.plot([x * 1.0 / 60 for x in xs], result, label='%d percentile' % percs[i])
pyplot.ylim([0, 3600])
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
