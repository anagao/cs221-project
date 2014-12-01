import algorithm, create_graph, hillclimb, util

def main():
    print 'main.py is calling util.load_grids()...'

    # Assumes create_graph.discretize_job_locations() has already been called,
    # so already created project_data/delivery_grid.pickle and pickup_grid.pickle
    pickup_grid, delivery_grid = util.load_grids() # returns (rounded lat, rounded lng) => [ {job1}, {job2} ]
    print 'util.load_grids() complete.'

    # a dictionary with key=(job1oid, job2oid) and value=total distance doing end(job1) -> start(job2) -> end(job2)
    #distance_matrix = create_graph.generate_distance_matrix(pickup_grid, delivery_grid)
    #print 'generate_distance_matrix() complete.'

    max_days = 5 # total number of days that the algorithm is creating a schedule for

    best_score, bestTour = hillclimb.hillclimb(#distance_matrix=distance_matrix, 
                                pickup_grid=pickup_grid, delivery_grid=delivery_grid,
                                start_lat=26.775, start_lng=-80.058, # Florida
                                max_days=max_days)
    util.printTour(bestTour)
    
    # br = algorithm.BestRoute(... distance_matrix, delivery_grid, max_days, ...)
    # bestPaths, pathScores = br.solve()

if __name__ == '__main__':
    main()
