"""
Basic greedy hill-climbing algorithm
@author Aaron Nagao
"""

import random, util

def get_initial_tour(pickup_grid, delivery_grid, start_lat, start_lng, max_days):
    """
    Randomly choose 1 job per day, up until max_days. Returns list of jobs.
    TODO: remove restriction that there is 1 job per day
    """
    initialTour = []
    lat, lng = start_lat, start_lng
    for i in xrange(max_days):
        job = random.choice( util.neighbors(pickup_grid, lat, lng, k=1) )
        initialTour.append(job)
        lng, lat = job['deliveryAddress']['location']['coordinates'] # note lat/lng switched
    return initialTour

def generate_swapped_tours(tour, pickup_grid, delivery_grid):
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

def hillclimb(pickup_grid, delivery_grid, start_lat, start_lng, max_days):
    """
    Hillclimb until we reach a local optima, or until MAX_ITERATIONS
    """
    bestTour = get_initial_tour(pickup_grid, delivery_grid, start_lat, start_lng, max_days)
    best_score = objective_function(bestTour)
    
    num_iterations = 0
    MAX_ITERATIONS = 1000
    
    while num_iterations < MAX_ITERATIONS:
        print "Current best: ",
        util.printTour(bestTour)

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

def objective_function(tour):
    """
    Takes a tour (list of job dicts), returns the value of this tour (bigger is better).
    TODO: incorporate gas, time
    TODO: objective_function = -inf if tour cannot be done in max_days
    """
    return sum( [job['price'] for job in tour] )
