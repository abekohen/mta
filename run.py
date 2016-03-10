from google.transit import gtfs_realtime_pb2
import urllib
import time
import traceback
from protobuf_to_dict import protobuf_to_dict
import itertools
import json
import random
import os

feed_ids = [1, 2, 11]
for i in itertools.count():
    if i > 0:
        delay = 2.0 + 5 * random.random()
        print 'sleeping %ss...' % delay
        time.sleep(delay)

    feed_id = feed_ids[i % len(feed_ids)]
    try:
        feed = gtfs_realtime_pb2.FeedMessage()
        response = urllib.urlopen('http://datamine.mta.info/mta_esi.php?key=%s&feed_id=%d' % (os.environ['MTA_KEY'], feed_id))
        feed.ParseFromString(response.read())
    except:
        traceback.print_exc()
        continue

    vehicles = [protobuf_to_dict(entity.vehicle) for entity in feed.entity if entity.HasField('vehicle')]
    print 'got', len(vehicles), 'vehicles'

    f = open('log.jsons', 'a')
    json.dump(vehicles, f)
    f.write('\n')
    f.close()


