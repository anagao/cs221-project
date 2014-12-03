import os
import json
import collections
import util
import random
import datetime

JOBS = os.path.join('project_data', 'jobs_pruned.json')
JOBS_WEEK = os.path.join('project_data', 'jobs_week_2014-09-26.json')

class Graph:
  """
  Usage:

  graph.distances_from(job_id): takes a String job_id, returns a dict of the job's neighbors
  graph.jobs[job_id]: dict, containing all relevant information about a job
  graph.pickup_grid, graph.delivery_grid: dicts from (int(lat), int(lng)) => ["jobid1", "jobid2", ...]
  """

  def __init__(self):
    self._load_jobs(JOBS_WEEK)
    self.pickup_grid, self.delivery_grid = util.load_grids()
    
  def distances_from(self, job1_id):
    ''' Returns <dict>distance
        distance.keys() are the neighbors of job_id
        distance[neighbor] = tuple(interjob_distance, intrajob_distance)
        interjob_distance = distance(end(job_id) -> start(neighbor))
        intrajob_distance = distance(start(neighbor) -> end(neighbor))
    '''
    distances = {}
    job1 = self.jobs[job1_id]
    for job2_id in util.neighbors(self.pickup_grid, *job1['delivery'], k=2):
      job2 = self.jobs[job2_id]
      if not self.is_after(job1, job2): continue

      d1 = util.distance(*job1['delivery']+job2['pickup']) #util.interjob_distance(job1, job2)
      d2 = util.distance(*job2['pickup']+job2['delivery'])

      distances[job2_id] = (d1, d2)

    return distances

  def get_price(self, job_id):
    job = self.jobs[job_id]
    return job['price']

  def get_distance(self, job1_id, job2_id):
    job1 = self.jobs[job1_id]
    job2 = self.jobs[job2_id]
    return util.distance(*job1['delivery']+job2['pickup'])

  def create_start_node(self, start_lat, start_lng):
    """
    Add a pseudo "START" job to graph and its internal data structures.
    @return <String> id = the id of this newly-created pseudo-job
    """
    job_id = "PSEUDO_START_JOB"
    
    # Add START to self.jobs
    self.jobs[job_id] = dict()
    self.jobs[job_id]['price'] = 0
    self.jobs[job_id]['pickup'] = (start_lat, start_lng)
    self.jobs[job_id]['delivery'] = (start_lat, start_lng)
    self.jobs[job_id]['date'] = 0

    return job_id

  def getRandomJobId(self):
    '''Returns a random job_id'''
    return random.choice(self.jobs.keys())

  def is_after(self, job1, job2):
    '''Checks if we can make it to job2'''
    start_time = datetime.datetime.fromtimestamp(job1['date']/1000)
    elapsed_time = self.drive_hours(util.distance(*job1['pickup']+job1['delivery']))
    current_time = start_time + datetime.timedelta(hours=elapsed_time)
    return current_time.date() <= datetime.date.fromtimestamp(job2['date']/1000)

  def drive_hours(self, distance):
    MILES_PER_HOUR = 65
    HOUR_PER_MILE = 1.0 / MILES_PER_HOUR
    MAX_HOURS_PER_DAY = 8
    hours = distance * HOUR_PER_MILE
    return (hours / MAX_HOURS_PER_DAY + (hours % MAX_HOURS_PER_DAY) / float(MAX_HOURS_PER_DAY)) * 24

  def _load_jobs(self, jobs_file):
    '''Private Function
       Creates self.jobs such that 
       @jobs[id]['price'] = value of trip
       @jobs[id]['pickup'] = pickup latlng
       @jobs[id]['delivery'] = delivery latlng
       @jobs[id]['date'] = pickup date 
    '''
    jobs = collections.defaultdict(dict)

    with open(jobs_file) as f:
      for line in f:
        job = json.loads(line)
        job_id = job['_id']['$oid']

        jobs[job_id]['price'] = job['price']

        (from_lng, from_lat) = job['pickupAddress']['location']['coordinates']
        (to_lng, to_lat) = job['deliveryAddress']['location']['coordinates']
        jobs[job_id]['pickup'] = (from_lat, from_lng)
        jobs[job_id]['delivery'] = (to_lat, to_lng)

        jobs[job_id]['date'] = job['pickupDate']

    self.jobs = dict(jobs)

