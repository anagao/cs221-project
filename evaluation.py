"""
Evaluation function, used in Depth-limited search
@author Aaron Nagao

Usage:
Then, if limited-depth tree search reaches its maximum depth,
call evaluation_function() to evaluate the value of choosing that state.
"""
from __future__ import division
import util

def evaluation_function(prevJob, nextJob, cur_days):
  """
  @param <dict> prevJob: the job I was just at
  @param <dict> nextJob: the job I am considering choosing
  @param <float> cur_days: the current number of days I have fulfilled, up to and including delivering prevJob

  @return <float> estimate of the value of choosing nextJob. Higher value = better choice.

  TODO: change manual weights of 1 to learned weights
  TODO: add more features

  Density of jobs within 50 mi of delivery location, average reward of jobs within 50mi,
  distance from end location, # days remaining,
  avg gas prices in the area
  """
  features = dict() # string featureName => (weight, featureValue) tuple

  # First, check whether I can finish this job on time
  # total cost of prevJob.end => nextJob.start => nextJob.end => home
  prevEnd_nextStart = 0
  nextStart_nextEnd = 0
  nextEnd_home = 0
  totalMilesNextJobAndHome = prevEnd_nextStart + nextStart_nextEnd + nextEnd_home
  totalDaysNextJobAndHome = (totalMilesNextJobAndHome / util.MPH) / 24
  if cur_days + totalDaysNextJobAndHome > totalNumDays:
    return float('-inf') # cannot take on this job
  
  # 1) Length of time to do this job
  totalMilesNextJob = prevEnd_nextStart + nextStart_nextEnd
  totalDaysNextJob = (totalMilesNextJob / util.MPH) / 24
  features['daysToDoJob'] = (-1, totalDaysNextJob)

  # 2) price of this job
  features['jobPrice'] = (1, nextJob['price'])

  # TODO: add other features
  (to_lng, to_lat) = job['deliveryAddress']['location']['coordinates']
  to_i, to_j = int(to_lat), int(to_lng)  
  numJobsInBucket = len( delivery_grid[(to_i, to_j)] )
  features['numJobsInBucket'] = (1, numJobsInBucket)

  return sum([ v[0]*v[1] for k,v in features.iteritems() ]) # dot product of feature and its weight
