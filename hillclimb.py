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
        job = random.choice( pickup_grid[(int(lat), int(lng))] )
        initialTour.append(job)
        lng, lat = job['deliveryAddress']['location']['coordinates'] # note lat/lng switched
    return initialTour

def generate_swapped_tours(tour, pickup_grid, delivery_grid):
    """
    Generates all possible tours which replaces one job with a different one.
    For now, only replace jobs with similar pickup location.
    TODO: include delivery location 
    """
    for i, job in enumerate(tour):
        pickup_lng, pickup_lat = job['pickupAddress']['location']['coordinates'] # note lat/lng switched
        for diffJob in pickup_grid[(int(pickup_lat), int(pickup_lng))]:
            if diffJob["_id"]["$oid"] == job["_id"]["$oid"]: continue # don't yield the same tour
            copy = tour[:]
            copy[i] = diffJob
            yield copy

def hillclimb(pickup_grid, delivery_grid, start_lat, start_lng, max_days):
    """
    Hillclimb until we reach a local optima, or until MAX_ITERATIONS
    """
    bestTour = get_initial_tour(pickup_grid, delivery_grid, start_lat, start_lng, max_days)
    best_score = objective_function(bestTour)
    
    num_iterations = 0
    MAX_ITERATIONS = 10
    
    while num_iterations < MAX_ITERATIONS:
        # examine moves around our current position
        move_made = False
        for nextTour in generate_swapped_tours(bestTour, pickup_grid, delivery_grid): # generator for all possible moves
            num_iterations += 1
            if num_iterations >= MAX_ITERATIONS:
                break
            
            # see if this move is better than the current
            next_score = objective_function(nextTour)
            
            if next_score > best_score:
                print "nextTour is better!"
                util.printTour(nextTour)

                bestTour = nextTour
                best_score = next_score
                move_made = True
                break # depth first search
            
        if not move_made:
            break # we couldn't find a better move (must be at a local maximum)
    
    return (best_score, bestTour)

def objective_function(tour):
    """
    Takes a tour (list of job dicts), returns the value of this tour (bigger is better).
    TODO: incorporate gas, time
    TODO: objective_function = -inf if tour cannot be done in max_days
    """
    return sum( [job['price'] for job in tour] )
