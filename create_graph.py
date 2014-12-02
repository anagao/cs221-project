import os
import json, pickle
import collections
import util

JOBS = os.path.join('project_data', 'jobs_pruned.json')
JOBS_WEEK = os.path.join('project_data', 'jobs_week_2014-09-26.json')

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
      pickup_grid[(from_i, from_j)].append(job['_id']['$oid'])

      # Add end location to delivery_grid
      (to_lng, to_lat) = job['deliveryAddress']['location']['coordinates']
      to_i, to_j = int(to_lat), int(to_lng)
      delivery_grid[(to_i, to_j)].append(job['_id']['$oid'])

  with open(os.path.join('project_data', 'pickup_grid.pickle'), 'wb') as pickup_out:
    pickle.dump(dict(pickup_grid), pickup_out)

  with open(os.path.join('project_data', 'delivery_grid.pickle'), 'wb') as delivery_out:
    pickle.dump(dict(delivery_grid), delivery_out)


def generate_distance_matrix(pickup_grid, delivery_grid, from_file=None):
  '''
  distance_matrix[job1id].keys() is all the neighbors of job1
  distance_matrix[job1id][job2id] = total distance doing end(job1) -> start(job2) -> end(job2)
  '''
  if from_file:
    return json.load(open(from_file))

  distance_matrix = collections.defaultdict(dict)
  
  print 'Building matrix...'
  progress, total =  0, sum(len(v) for v in delivery_grid.values())
  print total 

  for (start_lat, start_lng) in delivery_grid:
    neighbors = util.neighbors(pickup_grid, start_lat, start_lng, k=2)
    for job1 in delivery_grid[(start_lat, start_lng)]:
      util.print_progress(progress, total)
      for job2 in neighbors:
        if job2['pickupDate'] < job1['pickupDate']: continue

        d1 = util.interjob_distance(job1, job2)
        d2 = util.intrajob_distance(job2)

        distance_matrix[job1['_id']['$oid']][job2['_id']['$oid']] = d1 + d2

      progress += 1
  
  with open(os.path.join('project_data', 'distance_matrix.json'), 'w') as out:
    json.dump(distance_matrix, out) # Dump it so that we don't have to run this entire procedure again
  
  return distance_matrix

if __name__ == '__main__':
  discretize_job_locations(JOBS_WEEK)
  #generate_distance_matrix(*util.load_grids())
  # Use this once weve run this once: generate_distance_matric(None, None, from_file=os.path.join('project_data', 'distance_matrix.json'))
