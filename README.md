# Strava2GPX

A Python package to convert Strava activities using the Strava API to GPX format. Supports encoding heart rate, cadence, power (watts), and temperature data into GPX file using Garmin GpxExtensions format. Will not convert activity types without GPS data (e.g. Yoga, Weightlifting, etc.) Open a new issue to request additional features and report current problems or open a pull request if you want to contribute your own work.


## Installation

```sh
pip install strava2gpx
```
## Update

```sh
pip install --upgrade strava2gpx
```

## Usage Examples

### Write Activity by ID to GPX File
```python
from strava2gpx import strava2gpx
import asyncio

'''
Sends web requests so use in conjunction with asyncio 
or any other async library
'''

async def main():
    '''
    put in your Strava Api client_id, refresh_token, and client_secret
    '''
    client_id = '123456'
    refresh_token = 'adfh750a7s5df8a00dh7asdf98a9s8df6s9asdf8'
    client_secret = 'ahgdyt5672i3y8d345hgd2345c23hjgd1234yd23'

    # create an instance of strava2gpx
    s2g = strava2gpx(client_id, client_secret, refresh_token)

    # connect to Strava API
    await s2g.connect()

    # write activity to output.gpx by activity id
    await s2g.write_to_gpx(11893637629, "output")

if __name__ == '__main__':
    asyncio.run(main())
```

### Get a List of All User Activities
```python
from strava2gpx import strava2gpx
import asyncio
import os

async def main():
    '''
    put in your Strava Api client_id, refresh_token, and client_secret
    example using env variables
    '''
    client_id = os.getenv('STRAVA_CLIENT_ID')
    client_secret = os.getenv('STRAVA_CLIENT_SECRET')
    refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')

    # create an instance of strava2gpx
    s2g = strava2gpx(client_id, client_secret, refresh_token)

    # connect to Strava API
    await s2g.connect()

    # get a list of all user's Strava activities
    activities_list = await s2g.get_activities_list()

    '''
    Each list element is the following format
    [name, id, start_date, type]
    '''

    print(activities_list[0:5])

if __name__ == '__main__':
    asyncio.run(main())
```

#### Output
```
[
    ['Legs may be sore', 11910466229, '2024-07-17T11:57:21Z', 'Ride'],
    ['Tall Grass, Hidden Dirt', 11906994862, '2024-07-17T00:10:57Z', 'Ride'],
    ['A little thunder there, a little MTB here', 11898361818, '2024-07-16T01:16:13Z', 'Ride'],
    ['Morning Run', 11893637629, '2024-07-15T11:50:49Z', 'Run'],
    ['Afternoon Yoga', 11880523323, '2024-07-13T19:09:04Z', 'Yoga']
]
```
