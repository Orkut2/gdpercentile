import numpy as np
import pandas as pd
import urllib.request
import time

# get level list
# sort by ascending ratedplus rank
# extract top 150
# extract unique victors of each level
    # going in order so that only new victors are counted
    # also ensure that only 100% completions are counted

pointercrate_response100 = urllib.request.urlopen(urllib.request.Request("https://pointercrate.com/api/v2/demons/listed/?limit=100",headers={"User-Agent":"GD Percentile Calculator"}))
pointercrate100 = pd.read_json(pointercrate_response100)
pointercrate_response150 = urllib.request.urlopen(urllib.request.Request("https://pointercrate.com/api/v2/demons/listed/?limit=50&after=100",headers={"User-Agent":"GD Percentile Calculator"}))
pointercrate150 = pd.read_json(pointercrate_response150)

# full dump of all info on the top 150 levels
pointercrate_dump = pd.concat([pointercrate100, pointercrate150],ignore_index=True)

# filtered for only what i care about
ratedplus_filtered = pointercrate_dump[["id", "position", "name", "verifier"]]

# change verifier column from dictionary to only verifier name
ratedplus_filtered["verifier"] = ratedplus_filtered["verifier"].str["name"]

# iterate: for every entry in ratedplus_filtered,
    # add the verifier's name to the set of victors
    # if not a member, add the verifier's name as a victor
    # add all victors that are not in the set of victors

list_victors = set()
ratedplus_filtered["victors"] = None

for index, row in ratedplus_filtered.iterrows():
    victors_of_this_level = set()
    victors_of_this_level.add(row["verifier"])
    pointercrate_response_demondata = urllib.request.urlopen(urllib.request.Request(f"https://pointercrate.com/api/v2/demons/{row['id']}/",headers={"User-Agent": "GD Percentile Calculator"}))
    pointercrate_demondata = pd.read_json(pointercrate_response_demondata)
    pointercrate_victors = pointercrate_demondata["data"]["records"]
    for record in pointercrate_victors:
        if record["progress"] == 100:
            victors_of_this_level.add(record["player"]["name"])

    # filter victors that have beaten a harder level
    victors_of_this_level = victors_of_this_level - list_victors
    
    ratedplus_filtered.at[index, "victors"] = victors_of_this_level

    # add all victors that are not in the set of victors
    for victor in victors_of_this_level:
        list_victors.add(victor)
        # this is fine because adding an element already present in a set does nothing
    
    print(ratedplus_filtered.at[index, "victors"])
    time.sleep(0.4) # i reckon a website this small probably gets very few queries per day compared to other APIs but still, just to be polite

# write unique victor count to external file
with open("victors.txt", "w") as file:
    for index, row in ratedplus_filtered.iterrows():
        file.write ( f"{len(ratedplus_filtered.at[index, "victors"])}\n" )
    
