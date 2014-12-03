"""
Basic greedy hill-climbing algorithm
@author Aaron Nagao
"""
from __future__ import division
import random, util

class Hillclimb(object):

    MILES_PER_HOUR = 65
    HOUR_PER_MILE = 1.0 / MILES_PER_HOUR
    EMPTY_DOLLAR_PER_MILE = 1
    FULL_DOLLAR_PER_MILE = 2

    def __init__(self, graph, start_lat, start_lng, max_days):
        # Graph data structure
        self.graph = graph

        # user-defined parameters to algorithm
        self.start_lat = start_lat
        self.start_lng = start_lng
        self.max_days = max_days
                
        # algorithm data structures
        self.start_job_id = graph.create_start_node(start_lat, start_lng) # create pseudo-start node

    def get_initial_tour(self):
        """
        Randomly choose 1 job per day, up until max_days. Returns list of job ids.
        TODO: remove restriction that there is 1 job per day
        """
        curr_id = self.start_job_id
        initialTour = []
        #lat, lng = start_lat, start_lng
        #for i in xrange(max_days):
            #job = random.choice( util.neighbors(graph.pickup_grid, lat, lng, k=1) )
            #lng, lat = job['deliveryAddress']['location']['coordinates'] # note lat/lng switched

        while self.getStatistics(initialTour)[0] < self.max_days:
            neighbors = self.graph.distances_from(curr_id)
            nextjob_id = random.choice( neighbors.keys() )
            initialTour.append(nextjob_id)
            curr_id = nextjob_id
        return initialTour[:-1] # while loop breaks the first time that initialTour > max_days, so we chop off that last job

    def generate_swapped_tours(self, tour, pickup_grid, delivery_grid):
        """
        Generates possible tours, that replace one job with a different one.
        Algorithm: Since there are so many possible tours, swap out jobs randomly.

        For now, only replace jobs with similar pickup location.
        TODO: include delivery location 
        """
        MAX_SWAPS = 100
        for _ in xrange(MAX_SWAPS):
            index = random.randrange( len(tour) )
            job = tour[index]
            pickup_lng, pickup_lat = job['pickupAddress']['location']['coordinates'] # note lat/lng switched
            diffJob = random.choice( util.neighbors(pickup_grid, pickup_lat, pickup_lng, k=1) )
            
            # yield a new tour
            copy = tour[:]
            copy[index] = diffJob
            yield copy

    def hillclimbAlgorithm(self):
        """
        Hillclimb until we reach a local optima, or until MAX_ITERATIONS
        """
        bestTour = self.get_initial_tour()
        #util.printTour(graph, bestTour)
        return bestTour

        """
        best_score = objective_function(bestTour)
        
        num_iterations = 0
        MAX_ITERATIONS = 1000
        
        while num_iterations < MAX_ITERATIONS:
            print "Current best: ",
            util.printTour(graph, bestTour)

            # examine moves around our current position
            move_made = False
            for nextTour in generate_swapped_tours(bestTour, pickup_grid, delivery_grid): # generator for all possible moves
                num_iterations += 1
                if num_iterations >= MAX_ITERATIONS:
                    print "Reached MAX_ITERATIONS."
                    break
                
                # see if this move is better than the current
                next_score = objective_function(nextTour)
                
                if next_score > best_score:
                    bestTour = nextTour
                    best_score = next_score
                    move_made = True
                    break # depth first search
                
            if not move_made:
                print "None of the randomly-generated swaps were better than our current tour."
                break
        
        return (best_score, bestTour)
        """

    def objective_function(self, tour):
        """
        Takes a tour (list of job dicts), returns the value of this tour (bigger is better).
        TODO: incorporate gas, time
        TODO: objective_function = -inf if tour cannot be done in max_days
        """
        return sum( [job['price'] for job in tour] )

    def getStatistics(self, tour):
        """
        @param list of job ids. Does NOT include start_id
        @return (number of days to finish this tour, value of doing this tour)
        """
        if len(tour)==0:
            return (0,0)

        totalNumMiles, totalValue = 0, 0
        prevID = self.start_job_id

        for jobID in tour:
            currJob = self.graph.jobs[jobID]

            interjob_distance = self.graph.get_distance(prevID, jobID) # drive from prev job to this job            
            intrajob_distance = util.distance(*currJob['pickup']+currJob['delivery']) # do this job

            totalNumMiles += interjob_distance+intrajob_distance
            totalValue =  currJob['price'] - interjob_distance*Hillclimb.EMPTY_DOLLAR_PER_MILE - intrajob_distance*Hillclimb.FULL_DOLLAR_PER_MILE

            prevID = jobID
        
        totalNumMiles += self.graph.get_distance(jobID, self.start_job_id) # add the last job to home
        totalNumDays = totalNumMiles * Hillclimb.HOUR_PER_MILE / 24
        return (totalNumDays, totalValue)
