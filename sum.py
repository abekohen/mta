import json
import datetime
import seaborn
import numpy
from matplotlib import pyplot

stations = {}

for line in open('log.jsons'):
    for vehicle in json.loads(line.strip()):
        if vehicle.get('current_status') != 1: # STOPPED_AT
            continue
        key = (vehicle['trip']['route_id'], vehicle['stop_id'])
        timestamp = vehicle['timestamp'] # datetime.datetime.utcfromtimestamp(vehicle['timestamp'])
        stations.setdefault(key, set()).add(timestamp)

deltas = []
for key, values in stations.iteritems():
    last_value = None
    for value in sorted(values):
        if last_value is not None:
            deltas.append(value - last_value)
        last_value = value

print 'got', len(deltas), 'deltas'
seaborn.distplot([d for d in deltas if d < 3600])
pyplot.savefig('time_between_arrivals.png')

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
pyplot.ylim([0, max(offsets)*3])
pyplot.xlabel('Time you have waited for the subway')
pyplot.ylabel('Additional time until subway arrives')
pyplot.legend()
pyplot.savefig('time_until_arrival.png')
