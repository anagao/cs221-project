import sys, os
import matplotlib.pyplot as plt
import algorithm, Graph, hillclimb, util

def sensitivity_analysis(isHillclimb=False):
    """
    Vary the parameters to our algorithm, to increase their search space
    """
    def rand_trial():
        #(start_lat, start_lng) = graph.jobs[ graph.getRandomJobId() ]['pickup']
        (start_lat, start_lng) = (41, -74) # keep it constant across runs
        if isHillclimb:
            return hillclimb.Hillclimb(graph, start_lat, start_lng, max_days)
        else:
            return algorithm.BestRoute(graph, start_lat, start_lng, min_days, max_days)

    graph = Graph.Graph()
    print 'Graph Created'

    # ARTHUR: Quality results vs Speed tradeoff parameter
    N_TRIALS = 20 # For a certain parameter we're testing, number of trial runs to average over.

    # Parameter = max_days
    print 'Sensitizing number of days to schedule'
    maxdays_X = range(2, 11, 1) # ARTHUR: Edit 3-10
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
        max_days = 5 # constant across all trials

        print 'Sensitizing NUM_RUNS\n' # number of times to restart + rerun hillclimbing algorithm
        runs_X, runs_Y = range(1, 16), [] # 15
        for i, numRuns in enumerate(runs_X):
            util.print_progress(i, len(runs_X))
            trial_total = 0
            sys.stdout = open(os.devnull, "w") # Mute printing
            for trial in range(N_TRIALS):
                hc = rand_trial()
                hc.NUM_RUNS = numRuns
                bestTour = hc.hillclimbAlgorithm()
                (totalNumDays, totalValuePerDay) = hc.getStatistics(bestTour)
                trial_total += totalValuePerDay / util.MAX_HOURS_PER_DAY
            sys.stdout = sys.__stdout__ # Unmute printing
            runs_Y.append(trial_total / float(N_TRIALS))
        print 'NUM_RUNS: ', runs_X, runs_Y

        print 'Sensitizing MAX_SWAPS\n' # number of swaps to make on a tour before giving up
        swaps_X, swaps_Y = range(200, 2100, 200), []
        for i, numSwaps in enumerate(swaps_X):
            util.print_progress(i, len(swaps_X))
            trial_total = 0
            sys.stdout = open(os.devnull, "w") # Mute printing
            for trial in range(N_TRIALS):
                hc = rand_trial()
                hc.MAX_SWAPS = numSwaps
                bestTour = hc.hillclimbAlgorithm()
                (totalNumDays, totalValuePerDay) = hc.getStatistics(bestTour)
                trial_total += totalValuePerDay / util.MAX_HOURS_PER_DAY
            sys.stdout = sys.__stdout__ # Unmute printing
            swaps_Y.append(trial_total / float(N_TRIALS))
        print 'MAX_SWAPS', swaps_X, swaps_Y

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
    plt.figure()
    plt.plot(maxdays_X, maxdays_Y)
    plt.xlabel('Number of days to schedule')
    plt.ylabel('$ / hour worked')
    plt.title('Value vs. number of days to schedule')
    plt.savefig('valueVSnumDays.png')

    if isHillclimb:
        plt.figure()
        plt.plot(runs_X, runs_Y)
        plt.title('Value vs. number of hillclimbing restarts')
        plt.xlabel('Number of hillclimbing restarts')
        plt.ylabel('$ / hour worked')
        plt.savefig('valueVSnumRestarts.png')

        plt.figure()
        plt.plot(swaps_X, swaps_Y)
        plt.title('Value vs. number of random swaps')
        plt.xlabel('Number of random swaps')
        plt.ylabel('$ / hour worked')
        plt.savefig('valueVSnumSwaps.png')
    else:
        plt.plot(exploration_X, exploration_Y)
        plt.title('Value vs. beam size')
        plt.xlabel('Beam size k')
        plt.ylabel('$ / hour worked')
        plt.savefig('valueVSbeamSize.png')
        #plt.show()

        plt.plot(depth_X, depth_Y)
        plt.title('Value vs. depth limit')
        plt.xlabel('Recursive depth limit')
        plt.ylabel('$ / hour worked')
        plt.savefig('valueVSdepthLimit.png')
        #plt.show()

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

    locs = [(41, -74), (34, -118), (42, -87), (40, -75), (29, -99), (37, -122), (38, -86), (40, -83), (39, -77), (32, -106), (40, -105), (41, -82), (28, -83), (40, -80), (45, -93), (40, -76), (33, -112), (41, -74), (43, -89), (36, -79)]
    results_totalValue, results_valuePerHour = [], []
    for loc in locs:
        hc = hillclimb.Hillclimb(graph, start_lat=loc[0], start_lng=loc[1], max_days=5)
        bestTour = hc.hillclimbAlgorithm()
        #print "Final answer: "
        #util.printTour(graph, bestTour)
        
        (totalNumDays, totalValuePerDay) = hc.getStatistics(bestTour)
        results_totalValue.append(totalNumDays*totalValuePerDay)
        #print "Final number of days: " + str(totalNumDays)
        
        # e.g. $400/day ==> $400 / 8 hours working = $50/hr while on the job
        valuePerHour = totalValuePerDay / util.MAX_HOURS_PER_DAY
        #print "Final $/hour worked: " + str(valuePerHour)
        results_valuePerHour.append(valuePerHour)

    #print 'Results: total $ earned after 5 days (not necessarily driving for all 5 days)'
    #print results_totalValue

    print 'Results: $/hour (only counting hours worked)'
    print results_valuePerHour

    print 'Average $/hour: $',
    print sum(results_valuePerHour) / 20.0

if __name__ == '__main__':
    #algorithm()
    greedyHillClimbing()
    #sensitivity_analysis(isHillclimb=True)

