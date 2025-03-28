import requests
import json

base_url = "http://10.55.0.18:8080"
headers = {"Content-Type": "application/json"}


charging_rule = {
        'rule_name' : 'free_NVN',
        'qci' : 4,
        'arp_priority' : 5,
        'arp_preemption_capability' : True,
        'arp_preemption_vulnerability' : False,
        'mbr_dl' : 128000,
        'mbr_ul' : 128000,
        'gbr_dl' : 128000,
        'gbr_ul' : 128000,
        'tft_group_id' : 1,
        'precedence' : 100,
        'rating_group' : 20000
        }

print("Creating Charging Rule A")
r = requests.put(str(base_url) + '/charging_rule/', data=json.dumps(charging_rule), headers=headers)
print("Created Charging Rule ID: " + str(r.json()['charging_rule_id']))