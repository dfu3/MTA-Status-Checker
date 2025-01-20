# update_data.py

import requests
import json
from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict
from datetime import datetime
from pprint import pprint as pp

GTFS_URL = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs'
GTFS_URL_BASE = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/'
SUBWAY_FEEDS = [
    'nyct%2Fgtfs-ace',
    'nyct%2Fgtfs-g',
    'nyct%2Fgtfs-nqrw',
    'nyct%2Fgtfs',
    'nyct%2Fgtfs-bdfm',
    'nyct%2Fgtfs-jz',
    'nyct%2Fgtfs-l',
    'nyct%2Fgtfs-si',
]

DELAYS = dict()

def parse_delayed_lines(entity):
    lines = set()
    alert = entity['alert']
    if 'delay' in alert['header_text']['translation'][0]['text'].lower():
        if 'informed_entity' in alert:
            for trip in alert['informed_entity']:
                lines.add(trip['trip']['route_id'])

    return lines


def check_mta_delays(url):
    response = requests.get(url)

    if response.status_code == 200:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        feed_dict = protobuf_to_dict(feed)

        delayed_lines = set()
        if len(feed_dict['entity']) > 0:
            ent = feed_dict['entity'][-1]
            if 'alert' in ent:
                lines = parse_delayed_lines(ent)
                if lines:
                    delayed_lines = delayed_lines | lines
        

        print(delayed_lines)

    else:
        print(f"Error fetching data: HTTP {response.status_code}")


def update():
    for feed in SUBWAY_FEEDS:
        url = GTFS_URL_BASE + feed
        check_mta_delays(url)
    
    print(DELAYS)


update()