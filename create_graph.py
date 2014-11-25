import os
import json, pickle
import collections
import util

JOBS = os.path.join('project_data', 'jobs_pruned.json')
JOBS_WEEK = os.path.join('project_data', 'jobs_week_2014-09-26.json')

def generate_distance_matrix(pickup_grid, delivery_grid):
  '''
  Arjun: I haven't had the chance to run this and need to catch a flight now, so if one of you guys could run it that would be great.
  Hopefully we can do all that computation in memory (if not lower k-hop neighbors from 3 to 2).

  Returns a dictionary with key=(job1oid, job2oid)
  and value=total distance doing end(job1) -> start(job2) -> end(job2)
  '''
  distance_matrix = {}
  
  print 'Building matrix...'
  progress, total =  0, len(jobs)**2
  print total 

  for (start_lat, start_lng) in delivery_grid:
    for job in delivery_grid[start_loc]:
      for job2 in util.neighbors(pickup_grid, start_lat, start_lng, k=2):
        if job2['pickupDate'] < job1['pickupDate']: continue

        d1 = util.interjob_distance(job1, job2)
        d2 = util.intrajob_distance(job2)

        distance_matrix[(job1['_id']['$oid'], job2['_id']['$oid'])] = d1 + d2

  #json.dump(distance_matrix, 'distance_matrix.json')
  return distance_matrix # hopefully it fits in memory, else dump to json

def discretize_job_locations(jobs_file):
  '''
  We bucketize jobs by rounding each latitude and longitude to the nearest integer.
  This works well because 1 degree on earth corresponds to ~67.1 miles.
  So in order to look at everything within k*68 miles,
  we just have to look at k buckets around our current bucket.

  create_graph.py::discretize_job_locations() computed the grid and saved them to project data (Arjun sent the Dropbox link).
  Calling util.py::load_grids() takes approximately 2 minutes to load two 100mb files into memory.
  '''
  
  pickup_grid = collections.defaultdict(list)
  delivery_grid = collections.defaultdict(list)

  with open(jobs_file) as f:
    for line in f:
      job = json.loads(line)
      # Add start location to pickup_grid
      (from_lng, from_lat) = job['pickupAddress']['location']['coordinates']
      from_i, from_j = int(from_lat), int(from_lng)
      pickup_grid[(from_i, from_j)].append(job)

      # Add end location to delivery_grid
      (to_lng, to_lat) = job['deliveryAddress']['location']['coordinates']
      to_i, to_j = int(to_lat), int(to_lng)
      delivery_grid[(to_i, to_j)].append(job)

  with open(os.path.join('project_data', 'pickup_grid.pickle'), 'wb') as pickup_out:
    pickle.dump(dict(pickup_grid), pickup_out)

  with open(os.path.join('project_data', 'delivery_grid.pickle'), 'wb') as delivery_out:
    pickle.dump(dict(delivery_grid), delivery_out)


if __name__ == '__main__':
  discretize_job_locations(JOBS_WEEK)




# def generate_distance_matrix(jobs_file):
#   distance_matrix = {}
#   jobs = []
#   with open(jobs_file) as f:
#     for line in f:
#       job = json.loads(line)
#       jobs.append(job)
  
#   jobs = sorted(jobs, key=lambda job: job['pickupDate'])
#   print 'Sorted. Building matrix...'
#   progress, total =  0, len(jobs)**2
#   print total
#   for job1 in jobs:
#     for job2 in jobs:
#       if job2['pickupDate'] < job1['pickupDate']: continue
#       util.print_progress(progress, total); progress += 1

#       # Measure distance: job1_end --> job2_start --> job2_end
#       d1 = util.distance(job1['deliveryAddress']['location']['coordinates'][1], job1['deliveryAddress']['location']['coordinates'][0], \
#                     job2['pickupAddress']['location']['coordinates'][1], job2['pickupAddress']['location']['coordinates'][0])
#       if d1 > 300:
#         continue
#       d2 = util.distance(job2['pickupAddress']['location']['coordinates'][1], job2['pickupAddress']['location']['coordinates'][0], \
#                     job2['deliveryAddress']['location']['coordinates'][1], job2['deliveryAddress']['location']['coordinates'][0])
       
#       distance_matrix[(job1['_id']['$oid'], job2['_id']['$oid'])] = d1 + d2

#   json.dump(distance_matrix, 'distance_matrix.json')