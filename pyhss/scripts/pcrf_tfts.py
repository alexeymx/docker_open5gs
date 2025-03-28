import requests
import json

base_url = "http://10.55.0.18:8080"
headers = {"Content-Type": "application/json"}
# Define TFTs
tft_template1 = {
    'tft_group_id': 1,
    'tft_string': 'permit out 6 from 1.2.3.4 443 to any 1-65535',
    'direction': 1
}
tft_template2 = {
    'tft_group_id': 1,
    'tft_string': 'permit out 6 from any 1-65535 to 1.2.3.4 443',
    'direction': 2
}
print("Creating TFTs")
r = requests.put(str(base_url) + '/tft/', data=json.dumps(tft_template1), headers=headers)
r = requests.put(str(base_url) + '/tft/', data=json.dumps(tft_template2), headers=headers)