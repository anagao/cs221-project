import algorithm, Graph, hillclimb, util

def main():
    graph = Graph.Graph()
    print("made the graph successfully")
    # user-defined parameters
    start_lat, start_lng = 27, -80 # Florida=(27,-80)
    min_days = 1
    max_days = 5 # total number of days that the algorithm is creating a schedule for
    
    # Arthur's tree search algorithm
    br = algorithm.BestRoute(graph, start_lat, start_lng, min_days, max_days)
    bestPath = br.solve()
    print bestPath

def greedyHillClimbing():
    """
    Greedy hill-climbing algorithm (Aaron)
    """
    graph = Graph()
    pickup_grid, delivery_grid = graph.pickup_grid, graph.delivery_grid
    best_score, bestTour = hillclimb.hillclimb(
                                pickup_grid=pickup_grid, delivery_grid=delivery_grid,
                                start_lat=42, start_lng=-71, # Florida=(27,-80)
                                max_days=5)
    print "Final answer: ",
    util.printTour(bestTour)

if __name__ == '__main__':
    main()
