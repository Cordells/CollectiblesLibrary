# tally-microservice.py

import json

with open('main_save.json', 'r') as infile:
  collect_dict = json.load(infile)

cat_values = {}
total_value = 0
for category in collect_dict.values():
  cat_values[category["name"]] = 0
  for item in category["items"].values():
    cat_values[category["name"]] += item["value"]
    total_value += item["value"]

cat_values["Total"] = total_value
print(cat_values)
