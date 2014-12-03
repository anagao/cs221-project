"""
Converts jobs.json to jobs.csv, so CSV can be passed to TileMill visualization software.
@author Aaron Nagao
"""

import csv, json, os

def jsonToCSV():
  with open(os.path.join('project_data', 'jobs_week_2014-09-26.csv'), 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['longitude', 'latitude', 'price'])
    
    with open(os.path.join('project_data', 'jobs_week_2014-09-26.json')) as f:
      for line in f:
        job = json.loads(line)
        #pickupCoords = job["pickupAddress"]["location"]["coordinates"]
        price = job["price"]
        deliveryCoords = job["deliveryAddress"]["location"]["coordinates"]
        deliveryCoords.append(price)
        #writer.writerow(pickupCoords.append(price))
        writer.writerow(deliveryCoords)

if __name__ == '__main__':
    jsonToCSV()