import sys, os, math
try:
   import cPickle as pickle # faster because implemented in C
except:
   import pickle

MAX_HOURS_PER_DAY = 8.0
MILES_PER_HOUR = 65
HOUR_PER_MILE = 1.0 / MILES_PER_HOUR
LOAD_DELOAD_HOURS = 4
# Average cost per mile is $1.38 (http://www.thetruckersreport.com/infographics/cost-of-trucking/)
EMPTY_DOLLAR_PER_MILE = 1
FULL_DOLLAR_PER_MILE = 2

# Helper functions, used by both algorithm and hillclimb
def miles_to_drive_days(miles):
  return (miles*HOUR_PER_MILE + LOAD_DELOAD_HOURS) / float(MAX_HOURS_PER_DAY)

def compute_profit(price, interjob_distance, intrajob_distance):
  return price - interjob_distance*EMPTY_DOLLAR_PER_MILE - intrajob_distance*FULL_DOLLAR_PER_MILE



def print_progress(i, total):
  '''Print progress bar of i/total'''
  sys.stdout.write('\r')
  sys.stdout.write('{0: .3f}%'.format(float(i)/total*100))
  sys.stdout.flush()

def load_grids():
  '''Returns discretized grids of (int(lat), int(lng)) -> ["jobid1", "jobid2", ...]
     First return value is pickup location discretized.
     Second is dropoff location discretized.

     Assumes create_graph.py::discretize_job_locations() already computed the grid 
     and saved them to Dropbox/project_data/delivery_grid.pickle and pickup_grid.pickle.

     Note: We have a mean of ~155 jobs per node, with a standard 
           deviation of ~290 jobs for delivery and pickup grids.'''
  with open(os.path.join('project_data', 'pickup_grid.pickle'), 'rb') as pickup_in:
    pickup_grid = pickle.load(pickup_in)
  print "pickup_grid.pickle loaded."

  with open(os.path.join('project_data', 'delivery_grid.pickle'), 'rb') as delivery_in:
    delivery_grid = pickle.load(delivery_in)
  print "delivery_grid.pickle loaded."

  return pickup_grid, delivery_grid

def neighbors(grid, lat, lng, k=3):
  '''Returns all jobs within k discrete-degrees from (lat, lng).
     Note this is approximately a radius of k*67 miles'''
  neighbors = []
  for i in range(int(lat) - k, int(lat) + k+1):
    for j in range(int(lng) - k, int(lng) + k+1):
      if (i, j) in grid:
        neighbors.extend(grid[(i, j)])

  return neighbors

def distance(lat1, lng1, lat2, lng2):
    '''Returns geodesic distance between two points in miles.
       Uses great-circle (orthodromic) distance formulation'''
    lat1, lng1 = math.radians(lat1), math.radians(lng1)
    lat2, lng2 = math.radians(lat2), math.radians(lng2)

    earthRadius = 3958.75;
    dlong = lng2 - lng1
    dlat = lat2 - lat1
    a = (math.sin(dlat / 2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlong / 2))**2
    c = 2 * math.asin(min(1, math.sqrt(a)))
    dist = earthRadius * c
    return dist
 
def interjob_distance(job1, job2):
  '''Returns distance from end(job1) -> start(job2)'''
  (from_lng, from_lat) = job1['deliveryAddress']['location']['coordinates']
  (to_lng, to_lat) = job2['pickupAddress']['location']['coordinates']
  return distance(from_lat, from_lng, to_lat, to_lng)

def intrajob_distance(job):
  '''Returns length of a job'''
  (from_lng, from_lat) = job['pickupAddress']['location']['coordinates']
  (to_lng, to_lat) = job['deliveryAddress']['location']['coordinates']
  return distance(from_lat, from_lng, to_lat, to_lng)

def goto_job(start_lat, start_lng, job):
  '''Returns distance from a latlng to start of a job'''
  (to_lng, to_lat) = job['pickupAddress']['location']['coordinates']
  return distance(start_lat, start_lng, to_lat, to_lng)

def printTour(graph, tour):
  '''
  Pretty-prints a tour (list of job ids)
  '''
  totalPrice = 0
  for job_id in tour:
    job = graph.jobs[job_id]
    totalPrice += job["price"]
    print "#" + job_id[-3:] + ": " + "(%.2f,%.2f)"%job['pickup'] + " ==$" + str(job["price"]) + "==>" + "(%.2f,%.2f)"%job['delivery']
  # print "Total=$" + str(totalPrice)

"""
MPH = 70 # Average miles per hour
MPG = 6 # Miles per gallon (average semitruck)
PPG = 4 # $ per gallon of diesel
CPM = MPG * PPG # Cost per mile
"""