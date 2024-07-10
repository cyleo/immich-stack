# %%
# From: https://github.com/immich-app/immich/discussions/2479#discussioncomment-9249143 
import json
import requests

payload = json.dumps({
    "make": "SONY",
    "takenAfter": "2023-07-04T00:00:00.000Z",
    "takenBefore": "2023-07-05T00:00:00.000Z",
    "type": "IMAGE",
    # "withStacked": False
})
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'x-api-key': ''
}
base_url = ""
url = f"{base_url}/api/search/metadata"

# Get the data, api docs: https://immich.app/docs/api/search-metadata
# Returns 250 hits
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
            "PUT", url=f'{base_url}/api/assets', headers=headers, data=payload)
        # Remove duplicteID from JPG
        payload = json.dumps({
            "ids": [
                assets[fn.split(".")[0]+".jpg"]["id"]
            ],
            "duplicateId": None,
        })
        response = requests.request(
            "PUT", url=f'{base_url}/api/assets', headers=headers, data=payload)            
        # break  # remove if working as expected


# %%
