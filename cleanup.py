import datetime, collections, os, json, sys
import pickle
import math
import numpy
import matplotlib.pyplot as plt

JOBS = os.path.join('project_data', 'jobs_pruned.json')
JOBS_WEEK = os.path.join('project_data', 'jobs_week_2014-09-26.json')


def unique_jobs(jobs_file):
  prev_job = None
  with open(jobs_file + '_unique', 'w') as out:
    with open(jobs_file) as f:
      for line in f:
        job = json.loads(line)
        del job['_id'] # Many identical jobs, although job ids are different, so ignore this
        if prev_job != job: 
          prev_job = job
          out.write(line)

def get_date_counts(jobs_file):
  '''Returns a map of {date:# jobs in that date}'''
  date_counts = collections.Counter()
  with open(jobs_file) as f:
    for line in f:
      job = json.loads(line)
      date = datetime.date.fromtimestamp(job['pickupDate']/1000)
      date_counts[date] += 1

  return date_counts

def get_num_cities(jobs_file):
  from_cities = set([])
  to_cities = set([])
  with open(jobs_file) as f:
    for line in f:
      job = json.loads(line)
      from_cities.add(job['pickupAddress']['city'])
      to_cities.add(job['deliveryAddress']['city'])
  return len(from_cities), len(to_cities)

def get_num_zipcodes(jobs_file):
  from_zip = set([])
  to_zip = set([])
  with open(jobs_file) as f:
    for line in f:
      job = json.loads(line)
      from_zip.add(job['pickupAddress']['zipCode'])
      to_zip.add(job['deliveryAddress']['zipCode'])
  return len(from_zip), len(to_zip)


def get_week_jobs(jobs_file):
  date_counts = get_date_counts(jobs_file)
  START_INDEX = 10
  week = date_counts.keys()[START_INDEX:START_INDEX+7]
  outfile = 'unique_jobs_week_' + str(date_counts.keys()[START_INDEX])
  
  print 'Writing'

  with open(os.path.join('..', 'project_data', outfile), 'w') as out:
    with open(jobs_file) as f:
      for line in f:
        job = json.loads(line)
        date = datetime.date.fromtimestamp(job['pickupDate']/1000)
        if date in week:
          out.write(line)

def correct_latlngs(jobs_file):
  '''Make sure lnglats are (-, +) and in the contiguous US'''
  with open(jobs_file + '_corrected', 'w') as out:
    with open(jobs_file) as f:
      for line in f:
        job = json.loads(line)
        job['pickupAddress']['location']['coordinates'][1] = abs(job['pickupAddress']['location']['coordinates'][1])
        job['pickupAddress']['location']['coordinates'][0] = -abs(job['pickupAddress']['location']['coordinates'][0])
        job['deliveryAddress']['location']['coordinates'][1] = abs(job['deliveryAddress']['location']['coordinates'][1])
        job['deliveryAddress']['location']['coordinates'][0] = -abs(job['deliveryAddress']['location']['coordinates'][0])

        (lng1, lat1) = job['pickupAddress']['location']['coordinates']
        (lng2, lat2) = job['deliveryAddress']['location']['coordinates']
        
        # If we're not in the continguous US, kick them out.
        if min(lng1, lng2) < -125 or max(lng1, lng2) > -66 or min(lat1, lat2) < 24 or max(lat1, lat2) > 50:
          continue
        print >> out, json.dumps(job)

def get_minmax_latlng(jobs_file):
  min_lat, max_lat, min_lng, max_lng = float('inf'), -float('inf'), float('inf'), -float('inf')
  with open(jobs_file) as f:
    for line in f:
      job = json.loads(line)
      from_latlng = job['pickupAddress']['location']['coordinates']
      to_latlng = job['deliveryAddress']['location']['coordinates']
      min_lat = min(min_lat, from_latlng[1], to_latlng[1])
      max_lat = max(max_lat, from_latlng[1], to_latlng[1])
      min_lng = min(min_lng, from_latlng[0], to_latlng[0])
      max_lng = max(max_lng, from_latlng[0], to_latlng[0])

  return min_lng, max_lng, min_lat, max_lat


def check_distance_accuracy(jobs_file):
  distance_diffs = []
  c = 0
  total = 0
  with open(jobs_file) as f:
    for line in f:
      total += 1
      job = json.loads(line)
      if job['distanceInMiles'] <= 0: 
        c+= 1
        continue
      from_latlng = job['pickupAddress']['location']['coordinates']
      to_latlng = job['deliveryAddress']['location']['coordinates']
      geodesic_distance = distance(from_latlng[1], from_latlng[0], to_latlng[1], to_latlng[0])
      error = geodesic_distance/job['distanceInMiles']-1
      distance_diffs.append(error)

  print 'Missing distances: ', c/float(total)
  print 'Mean: ', numpy.mean(distance_diffs)
  print 'Stdev: ', numpy.std(distance_diffs)

  values = [int(p*100) for p in distance_diffs]
  counts = collections.Counter(values)
  X = sorted(counts.keys())
  Y = [counts[x] for x in X]
  

  fig = plt.figure()
  ax = fig.add_subplot(111)
  ax.plot(X, Y)
  ax.set_title('[Geodesic distance - Actual Distance] histogram')
  ax.set_xlabel('Miles')
  ax.set_ylabel('Count')
  plt.show()