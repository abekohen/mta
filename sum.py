import json
import datetime
import seaborn
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

seaborn.distplot(deltas)
pyplot.savefig('deltas.png')
# pyplot.show()
