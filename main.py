import sys, os
import matplotlib.pyplot as plt
import algorithm, Graph, hillclimb, util, random

def sensitivity_analysis(isHillclimb=False):
    def rand_trial():
        rand_id = graph.getRandomJobId()
        (start_lat, start_lng) = graph.jobs[rand_id]['pickup']
        if isHillclimb:
            return hillclimb.Hillclimb(graph, start_lat, start_lng, max_days)
        else:
            return algorithm.BestRoute(graph, start_lat, start_lng, min_days, max_days)

    graph = Graph.Graph()
    print 'Graph Created'

    N_TRIALS = 5 # ARTHUR: Quality results vs Speed tradeoff parameter

    # Parameter = max_days
    print 'Sensitizing Max Days'
    maxdays_X = range(3, 10) # ARTHUR: Edit
    maxdays_Y = []
    min_days = 1
    for i, max_days in enumerate(maxdays_X):
        util.print_progress(i, len(maxdays_X))
        trial_total = 0
        sys.stdout = open(os.devnull, "w") # Mute printing
        for trial in range(N_TRIALS):
            if isHillclimb:
                hc = rand_trial()
                bestTour = hc.hillclimbAlgorithm()
                (totalNumDays, totalValuePerDay) = hc.getStatistics(bestTour)
                trial_total += totalValuePerDay / util.MAX_HOURS_PER_DAY
            else:
                br = rand_trial()
                trial_total += max(br.solve()) # ARTHUR: divide by trip length here
        
        sys.stdout = sys.__stdout__ # Unmute printing
        maxdays_Y.append(trial_total / float(N_TRIALS))

    print
    print 'Days', maxdays_X, maxdays_Y

    if isHillclimb:
        pass
    else:
        # Parameter = explore_edges
        print 'Sensitizing EXPLORE_EDGES'
        exploration_X = range(10, 15) #ARTHUR: Edit
        exploration_Y = []
        min_days = 1
        max_days = 7
        for i, exploration in enumerate(exploration_X):
            util.print_progress(i, len(exploration_X))
            trial_total = 0
            sys.stdout = open(os.devnull, "w") # Mute printing
            for trial in range(N_TRIALS):
                br = rand_trial()
                br.EXPLORE_EDGES = exploration
                trial_total += max(br.solve()) # ARTHUR: divide by trip length here
            
            sys.stdout = sys.__stdout__ # Unmute printing
            exploration_Y.append(trial_total / float(N_TRIALS))

        print
        print 'Exploration', exploration_X, exploration_Y

        # Parameter = FIND_NODE_DEPTH
        print 'Sensitizing FIND_NODE_DEPTH'
        depth_X = range(1, 5) # ARTHUR: Edit
        depth_Y = []
        min_days = 1
        max_days = 7
        for i, node_depth in enumerate(depth_X):
            util.print_progress(i, len(depth_X))
            trial_total = 0
            sys.stdout = open(os.devnull, "w") # Mute prnting
            for trial in range(N_TRIALS):
                br = rand_trial()
                br.FIND_NODE_DEPTH = node_depth
                trial_total += max(br.solve()) # ARTHUR: divide by trip length here
            
            sys.stdout = sys.__stdout__ #Unmute prnting
            depth_Y.append(trial_total / float(N_TRIALS))

        print
        print 'Depth', depth_X, depth_Y
    
    # Plot results
    plt.plot(maxdays_X, maxdays_Y)
    plt.title('Value over Max Trip Length')
    plt.show()

    if isHillclimb:
        pass
    else:
        plt.plot(exploration_X, exploration_Y)
        plt.title('Value over Exploration Width')
        plt.show()

        plt.plot(depth_X, depth_Y)
        plt.title('Value over Depth')
        plt.show()

def algorithm():
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
    #algorithm()
    #greedyHillClimbing()
    sensitivity_analysis(isHillclimb=False)

