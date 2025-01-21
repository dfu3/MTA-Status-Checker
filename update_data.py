# update_data.py

import requests
from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict
from datetime import datetime

GTFS_URL_BASE = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/'
SUBWAY_FEEDS = [
    'nyct%2Fgtfs-ace',
    'nyct%2Fgtfs-g',
    'nyct%2Fgtfs-nqrw',
    'nyct%2Fgtfs', # this is the only feed that seems to return alert data...
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
    delayed_lines = set()
    if response.status_code == 200:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        feed_dict = protobuf_to_dict(feed)

        
        if len(feed_dict['entity']) > 0:
            # alert entity is always last
            ent = feed_dict['entity'][-1]
            if 'alert' in ent:
                delayed_lines = parse_delayed_lines(ent)

    else:
        print(f"Error fetching data: HTTP {response.status_code}")

    return delayed_lines


def update():
    delayed_lines = set()
    req_time = datetime.now()
    for feed in SUBWAY_FEEDS:
        url = GTFS_URL_BASE + feed
        delayed_lines = delayed_lines | check_mta_delays(url)
    
    diff = set(DELAYS.keys()) - delayed_lines
    for line in diff: 
        if DELAYS[line]['currently_delayed']:
            DELAYS[line]['currently_delayed'] = False
            DELAYS[line]['total_delayed'] += (req_time - DELAYS[line]['delay_start']).total_seconds()
            print(f'Line {line} is is now recovered')

    for line in delayed_lines:
        if line not in DELAYS:
            DELAYS[line] = {
                'delay_start': req_time,
                'total_delayed': 0,
                'currently_delayed': True,
            }
            print(f'Line {line} is experiencing delays')
        elif line in DELAYS and not DELAYS[line]['currently_delayed']:
            DELAYS[line]['currently_delayed'] = True
            DELAYS[line]['delay_start'] = req_time
            print(f'Line {line} is experiencing delays')

