# %%
# From: https://github.com/immich-app/immich/discussions/2479#discussioncomment-9249143
import json
import requests
from datetime import datetime

# Variables
BASE_URL = ''
API_KEY = ''
START_DATE = '1990-01-01T00:00:00.000Z'

# Constants
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'x-api-key': f'{API_KEY}'
}
url = f"{BASE_URL}/api/search/metadata"

# Start processing, initialize last_processed
last_processed = 0

for i in range(5):

    if last_processed == 0:
        taken_before = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    else:
        taken_before = last_processed

    payload = json.dumps({
        'make': 'SONY',
        'takenAfter': f'{START_DATE}',
        'takenBefore': f'{taken_before}',
        'type': 'IMAGE',
        "withStacked": False
    })

    # Get the data, api docs: https://immich.app/docs/api/search-metadata
    # Returns 250 hits, new to old(?)
    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)
    assets = {a["originalFileName"]: a for a in data['assets']['items']}

    # Find if a jpg and raw are in the same batch. API docs: https://immich.app/docs/api/update-assets
    for fn, a in assets.items():
        if fn[-3:].lower() == "arw" and fn.split(".")[0]+".jpg" in assets:
            print(
                f'Match found:{fn}, {assets[fn.split(".")[0]+".jpg"]["originalFileName"]}')
            # Set JPG as stackparent for the raw file, remove duplicteID
            payload = json.dumps({
                "ids": [
                    a["id"]
                ],
                "duplicateId": None,
                "stackParentId": assets[fn.split(".")[0]+".jpg"]["id"]
            })
            response = requests.request(
                "PUT", url=f'{BASE_URL}/api/assets', headers=headers, data=payload)
            # Remove duplicteID from JPG
            payload = json.dumps({
                "ids": [
                    assets[fn.split(".")[0]+".jpg"]["id"]
                ],
                "duplicateId": None,
            })
            response = requests.request(
                "PUT", url=f'{BASE_URL}/api/assets', headers=headers, data=payload)

    # Find the last processed id
    file_created_at_values = [entry['fileCreatedAt']
                              for entry in assets.values()]
    file_created_at_dates = [datetime.strptime(
        value, '%Y-%m-%dT%H:%M:%S.%fZ') for value in file_created_at_values]
    last_processed = min(file_created_at_dates).strftime(
        "%Y-%m-%dT%H:%M:%S.000Z")
