import os
import json
import collections
import util
import random

JOBS = os.path.join('project_data', 'jobs_pruned.json')
JOBS_WEEK = os.path.join('project_data', 'jobs_week_2014-09-26.json')

class Graph:  
  def __init__(self):
    self._load_jobs(JOBS_WEEK)
    self.pickup_grid, self.delivery_grid = util.load_grids()
    
  def distances_from(self, job1_id):
    ''' Returns @distance
        distance.keys() are the neighbors of job_id
        distance[neighbor] = tuple(interjob_distance, intrajob_distance)
        interjob_distance = distance(end(job_id) -> start(neighbor))
        intrajob_distance = distance(start(neighbor) -> end(neighbor))
    '''
    distances = {}
    job1 = self.jobs[job1_id]
    for job2_id in util.neighbors(self.pickup_grid, *job1['delivery'], k=2):
      job2 = self.jobs[job2_id]
      if job2['date'] < job1['date']: continue

      d1 = util.distance(*job1['delivery']+job2['pickup']) #util.interjob_distance(job1, job2)
      d2 = util.distance(*job2['pickup']+job2['delivery'])

      distances[job2_id] = (d1, d2)

    return distances

  def create_start_node(self, start_lat, start_lng):
    """
    Add a pseudo "START" job to this graph, and all its internal data structures.
    @return <String> id = the id of this newly-created pseudo-job
    """
    job_id = "PSEUDO_START_JOB"
    
    # Add START to self.jobs
    self.jobs[job_id] = dict()
    self.jobs[job_id]['price'] = 0
    self.jobs[job_id]['pickup'] = None
    self.jobs[job_id]['delivery'] = (start_lat, start_lng)
    self.jobs[job_id]['date'] = 0

    return job_id

  def getRandomJobId(self):
    '''Returns a random job_id'''
    return random.choice(self.jobs.keys())

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
