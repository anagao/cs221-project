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
    graph = Graph.Graph()
    hc = hillclimb.Hillclimb(graph,
                                start_lat=27, start_lng=-80, # (42,-71) also valid
                                max_days=5)
    bestTour = hc.hillclimbAlgorithm()
    print "Final answer: "
    util.printTour(graph, bestTour)
    
    (totalNumDays, totalValue) = hc.getStatistics(bestTour)
    print "Final number of days: " + str(totalNumDays)
    print "Final value: $" + str(totalValue)
    print "Final $/hour: " + str(totalValue / totalNumDays / 24)

if __name__ == '__main__':
    main()
    #greedyHillClimbing()
