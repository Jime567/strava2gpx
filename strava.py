import aiohttp
import aiofiles
import asyncio
import os

class strava2gpx:
    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        self.activities_list = None
        self.streams = {
                        "latlng": 1, 
                        "altitude": 1, 
                        "heartrate": 0, 
                        "cadence": 0, 
                        "watts": 0, 
                        "temp": 0}

    async def connect (self):
        self.access_token = await self.refresh_access_token()

    async def get_activities_list(self):
            activities = await self.get_strava_activities(1)
            masterlist = [[activity['name'], activity['id'], activity['start_date'], activity['type']] for activity in activities]
            print("Received " + str(len(masterlist)) + " activities")
            page = 1
            while len(activities) != 0:
                page += 1
                activities = await self.get_strava_activities(page)
                masterlist.extend([[activity['name'], activity['id'], activity['start_date'], activity['type']] for activity in activities])
                print("Received " + str(len(masterlist)) + " activities")
            return masterlist
    
    async def refresh_access_token(self):
        token_endpoint = 'https://www.strava.com/api/v3/oauth/token'

        form_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(token_endpoint, data=form_data) as response:
                    if response.status != 200:
                        if response.status == 401:
                            raise Exception('401 Unauthorized: Check Client ID, Client Secret, and Refresh Token')
                        else:
                            raise Exception('Failed to refresh access token')
                    data = await response.json()
                    self.access_token = data['access_token']
                    return self.access_token
            except Exception as e:
                print('Error refreshing access token:', str(e))
                raise

    async def get_strava_activities(self, page):
        api_url = 'https://www.strava.com/api/v3/athlete/activities'
        query_params = 'per_page=200'

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{api_url}?{query_params}&page={page}', headers={
                    'Authorization': f'Bearer {self.access_token}'
                }) as response:
                    if response.status != 200:
                        raise Exception('Failed to get activities')

                    data = await response.json()
                    return data
        except Exception as e:
            print('Error getting activities:', str(e))
            raise

    async def get_data_stream(self, activity_id):
        api_url = f'https://www.strava.com/api/v3/activities/{activity_id}/streams'
        query_params = 'time'
        for key, value in self.streams.items():
            if value == 1:
                query_params += f',{key}'
        url = f'{api_url}?keys={query_params}&key_by_type=true'

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={
                    'Authorization': f'Bearer {self.access_token}'
                }) as response:
                    if response.status != 200:
                        raise Exception('Failed to get data stream')

                    data = await response.json()
                    return data
        except Exception as e:
            print('Error getting data streams:', str(e))
            raise

    async def get_strava_activity(self, activity_id):
        api_url = 'https://www.strava.com/api/v3/activities/'
        url = f'{api_url}{activity_id}?include_all_efforts=false'
        print(url)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={
                    'Authorization': f'Bearer {self.access_token}'
                }) as response:
                    if response.status != 200:
                        raise Exception('Failed to get activity')

                    data = await response.json()
                    return data
        except Exception as e:
            print('Error getting activity:', str(e))
            raise

    async def detect_activity_streams(self, activity):
        if activity['device_watts'] == True:
            self.streams['watts'] = 1
        else:
            self.streams['watts'] = 0
        if activity['has_heartrate'] == True:
            self.streams['heartrate'] = 1
        else:
            self.streams['heartrate'] = 0
        if 'average_cadence' in activity:
            self.streams['cadence'] = 1
        else:
            self.streams['cadence'] = 0
        if 'average_temp' in activity:
            self.streams['temp'] = 1
        else:
            self.streams['temp'] = 0

    async def add_seconds_to_timestamp(self, start_timestamp, seconds):
        from datetime import datetime, timedelta
        start_time = datetime.fromisoformat(start_timestamp.replace("Z", "+00:00"))
        new_time = start_time + timedelta(seconds=seconds)
        return new_time.isoformat() + "Z"

    async def gpx_writer(self, activity):
        gpx_content_start = f'''<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://www.topografix.com/GPX/1/1 
http://www.topografix.com/GPX/1/1/gpx.xsd 
http://www.garmin.com/xmlschemas/GpxExtensions/v3 
http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd 
http://www.garmin.com/xmlschemas/TrackPointExtension/v1 
http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd" 
creator="StravaGPX" version="1.1" 
xmlns="http://www.topografix.com/GPX/1/1" 
xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3">
<metadata>
<time>{activity[2]}</time>
</metadata>
<trk>
<name>{activity[0]}</name>
<type>{activity[3]}</type>
<trkseg>
'''

        gpx_content_end = '''
</trkseg>
</trk>
</gpx>
'''

        try:
            async with aiofiles.open('build.gpx', 'w') as f:
                await f.write(gpx_content_start)

            data_streams = await self.get_data_stream(activity[1])

            if data_streams['latlng']['original_size'] != data_streams['time']['original_size']:
                print("Error: latlng does not equal Time")
                return

            trkpts = []
            for i in range(data_streams['time']['original_size']):
                time = await self.add_seconds_to_timestamp(activity[2], data_streams['time']['data'][i])
                trkpt = f'''
<trkpt lat="{float(data_streams['latlng']['data'][i][0]):.7f}" lon="{float(data_streams['latlng']['data'][i][1]):.7f}">
<ele>{float(data_streams['altitude']['data'][i]):.1f}</ele>
<time>{time}</time>
<extensions>
<gpxtpx:TrackPointExtension>
<gpxtpx:hr>{data_streams['heartrate']['data'][i]}</gpxtpx:hr>
</gpxtpx:TrackPointExtension>
</extensions>
</trkpt>
'''
                trkpts.append(trkpt)

            async with aiofiles.open('build.gpx', 'a') as f:
                await f.write(''.join(trkpts))
                await f.write(gpx_content_end)

            print('GPX file saved successfully.')
        except Exception as err:
            print('Error writing GPX file:', str(err))

async def main():
    print("Starting Strava2GPX")
    client_id = os.getenv('STRAVA_CLIENT_ID')
    client_secret = os.getenv('STRAVA_CLIENT_SECRET')
    refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')

    s2g = strava2gpx(client_id, client_secret, refresh_token)
    await s2g.connect()
    act = await s2g.get_strava_activity(591201341)
    await s2g.detect_activity_streams(act)
    data = await s2g.get_data_stream(591201341)
    print(data)
    # s2g.activities_list = await s2g.get_activities_list()
    # print(s2g.activities_list[0])

    # print("Refresh Token:", s2g.refresh_token)
    # print(len(s2g.activities_list), "Activities Found")

    # Example usage:
    # await s2g.gpx_writer(activity)

    # You can call other methods of s2g here as needed

if __name__ == '__main__':
    asyncio.run(main())
