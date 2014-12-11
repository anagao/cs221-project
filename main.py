import algorithm, Graph, hillclimb, util

def main():
    graph = Graph.Graph()
    print("made the graph successfully")
    # user-defined parameters
    start_lat, start_lng = 44, -116 # Florida=(27,-80)
    min_days = 1
    max_days = 5 # total number of days that the algorithm is creating a schedule for
    
    # Arthur's tree search algorithm
    print("starting brant knuth")
    br = algorithm.BestRoute(graph, start_lat, start_lng, min_days, max_days)
    path_profit = br.solve()
    print path_profit

def greedyHillClimbing():
    """
    Greedy hill-climbing algorithm (Aaron)
    """
    graph = Graph.Graph()
    hc = hillclimb.Hillclimb(graph,
                                start_lat=27, start_lng=-80, # (42,-71) also valid
                                max_days=7)
    bestTour = hc.hillclimbAlgorithm()
    print "Final answer: "
    util.printTour(graph, bestTour)
    
    (totalNumDays, totalValuePerDay) = hc.getStatistics(bestTour)
    print "Final number of days: " + str(totalNumDays)
    
    # e.g. $400/day ==> $400 / 8 hours working = $50/hr while on the job
    print "Final $/hour worked: " + str(totalValuePerDay / util.MAX_HOURS_PER_DAY)

if __name__ == '__main__':
    #main()
    greedyHillClimbing()
