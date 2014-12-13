"""
Greedy hill-climbing algorithm: start with a tour and randomly swap out jobs.

@author Aaron Nagao
"""
from __future__ import division
import random, util

class Hillclimb(object):

    def __init__(self, graph, start_lat, start_lng, max_days):
        # user-defined parameters to algorithm
        self.start_lat = start_lat
        self.start_lng = start_lng
        self.max_days = max_days

        # algorithm parameters to tweak
        # increase these parameters for wider search space but longer runtime
        self.NUM_RUNS = 10 # number of times to restart + rerun hillclimbing algorithm
        self.MAX_SWAPS = 1000 # number of swaps to make on a single tour before giving up
                
        # algorithm data structures
        self.graph = graph # Graph data structure
        self.start_job_id = graph.create_start_node(start_lat, start_lng) # create pseudo-start node

    def get_initial_tour(self):
        """
        Randomly return some initialTour, that is slightly longer than max_days. 
        Returns list of job ids.
        """
        curr_id = self.start_job_id
        initialTour = []
        
        while self.getStatistics(initialTour)[0] < self.max_days:
            neighbors = self.graph.distances_from(curr_id)
            if not neighbors: # edge case: if the job we picked has no neighbors
                # backtrack one step. continue = let while loop randomly pick a different neighbor
                initialTour.pop()
                curr_id = initialTour[-1] if initialTour else self.start_job_id
                continue
            nextjob_id = random.choice( neighbors.keys() )
            initialTour.append(nextjob_id)
            curr_id = nextjob_id
        
        # initialTour[:-1] is valid: while loop breaks the first time that initialTour > max_days, so we chop off that last job
        # however, return a slightly-longer but invalid tour, so that we have more potential swaps
        return initialTour

    def generate_swapped_tours(self, tour):
        """
        Yield MAX_SWAPS new tours, such that ONE job of @tour is replaced with a different one.
        Algorithm: Since there are so many possible new tours, swap out jobs randomly.
        Search space: Swap out jobs with similar pickup location or delivery location (50/50 split)
        """
        for _ in xrange(self.MAX_SWAPS):
            # randomly choose a list index to swap out
            index = random.randrange( len(tour) )
            job_id = tour[index]

            # search for a different job with the same pickup/delivery location
            if random.random() < 0.5:
                pickup_lat, pickup_lng = self.graph.jobs[job_id]['pickup']
                diffJob = random.choice( util.neighbors(self.graph.pickup_grid, pickup_lat, pickup_lng, k=1) )
            else:
                delivery_lat, delivery_lng = self.graph.jobs[job_id]['delivery']
                diffJob = random.choice( util.neighbors(self.graph.delivery_grid, delivery_lat, delivery_lng, k=1) )
            
            # yield a new tour
            copy = tour[:]
            copy[index] = diffJob # swap out job at index for diffJob
            yield copy

    def hillclimbAlgorithm(self):
        """
        Run hillclimbing algorithm NUM_RUNS times.
            On each run, hillclimb until none of the swapped tours are better than the one we have 
            (i.e. a local optima), or until MAX_ITERATIONS
        Return the best tour over the NUM_RUNS
        """
        bestTour_overall = []
        best_value_overall = float('-inf')
        for run in xrange(self.NUM_RUNS):

            bestTour = self.get_initial_tour()
            best_value = self.getStatistics(bestTour)[1] # $/day
            
            num_iterations = 0
            MAX_ITERATIONS = 10000 # stop early even if it hasn't converged yet (for runtime reasons)
            while num_iterations < MAX_ITERATIONS:
                #print "Current best: "
                #util.printTour(self.graph, bestTour)

                # examine moves around our current position
                move_made = False
                for nextTour in self.generate_swapped_tours(bestTour): # generator for all possible moves
                    num_iterations += 1
                    if num_iterations >= MAX_ITERATIONS:
                        print "Reached MAX_ITERATIONS."
                        break
                    
                    # see if this move is better than the current
                    next_value = self.getStatistics(nextTour)[1]
                    if next_value > best_value:
                        bestTour, best_value = nextTour, next_value
                        move_made = True
                        break # depth first search
                    
                if not move_made:
                    #print "None of the randomly-generated swaps were better than our current tour."
                    break

            # finished one run of hillclimbing. Compare to global best overall
            #print "Best tour on iteration " + str(run) + ": $" + str(best_value) + "/day"
            if best_value > best_value_overall:
                bestTour_overall, best_value_overall = bestTour, best_value

        return bestTour_overall

    def getStatistics(self, tour):
        """
        @param list of job ids. Does NOT include start_id
        @return (number of days to finish this tour, value of doing this tour in $/day)
        """
        if len(tour)==0:
            return (0,0)

        totalNumDays, totalValue = 0, 0
        prevID = self.start_job_id

        for jobID in tour:
            currJob = self.graph.jobs[jobID]

            interjob_distance = self.graph.get_distance(prevID, jobID) # drive from prev job to this job            
            intrajob_distance = util.distance(*currJob['pickup']+currJob['delivery']) # do this job

            totalNumDays += util.miles_to_drive_days( interjob_distance+intrajob_distance )
            totalValue += util.compute_profit(currJob['price'], interjob_distance, intrajob_distance)

            prevID = jobID
        
        # add # of days from the last job to home
        totalNumDays += util.miles_to_drive_days( self.graph.get_distance(jobID, self.start_job_id) )

        if totalNumDays > self.max_days:
            totalValue = float('-inf')
        return (totalNumDays, totalValue/totalNumDays)
