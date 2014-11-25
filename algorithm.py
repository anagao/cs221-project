import numpy, Queue

"""
BestRoute is a class that expects 
Input:
	Graph: A graph with the following properties:
		We require that once a truck picks up a load, it must drop it off
		befroe picking up another load. Thus, we can think of a full path as
		start -> pickup1 -> dropoff1 -> pickup2 -> dropoff2 -----> end 
		and model this graph as having the following features:
		pickup nodes, lat,long, which only have an edge to the respective dropoff location
			and have cost = -1 * price of gas/wear tear for number of miles
		dropoff nodes, lat, long, which have edges to all pickup nodes
			and have coest -1 * price of gas/wear tear for number of miles + price of job.
			It will also have a special 'end' edge, with the -1 * cost of gas + wear and tear
		start_node, lat, long, which has edges to all pickup locaitons -1 * price of gas/wear tear for number of miles

		However, we must simplify the graph to be able to be run on 16GB of memory.
		First, the graph must be heavily pruned, not allowing drivers to drive more than X miles
		to a pickup location, thus the number of edges will be reduced considerably.
		Next, because we require that a picked up load must be dropped off before picking
		up another load, we can simplify this graph by having an edge signify going from once
		dropoff location to another dropoff location, with an edge cost of 
		-1 * gas/wear and tear to get to dropoff location1 to pickup location 2 +
		-1 * gas/wear and tear to get to pickup location 2 to dropoff location 2 +
		price of the job. Thus our graph looks as follows. We will also have the special end edge.
		start ------------------> x1 ------------------> x2 -----> end

		g.start_node() returns the node of the trip start location
		g.end_node() returns the node of the trip end location..not necessarily the same

		A node will have the following:
			list of edges
			home edge
		An edge will have the following
			price (positive is good)
			time  (days)
			prevNode
			nextNode


	heur_data:
		heur_data is a map that contains the data for the heuristic.
		key=price_grid
		key=job_density_grid


	Min_days: The minimum number of days that a trip can last.
	Max_days: The maximum number of days that a trip can last.
	Start_latitude: the latitude of the starting location for the truck
	Start_longitude: the longitude of the starting locaiton for the truck

"""
class BestRoute(object):
	PROFIT_THRESHOLD = 100
	EXPLORE_EDGES = 100
	FIND_NODE_DEPTH = 4
	HEURISTIC_WEIGHTS = [1, 1, 1]

	def __init__(self, graph, heur_data, min_days, max_days):
		self.graph = graph
		self.heur_data = heur_data
		self.min_days = min_days
		self.max_days = max_days
		self.bestScore = -1 *float('inf')
		self.bestPaths = []
		self.pathScores = []



	"""
	solve
	A wrapper function that attempts to find the best path for to maximize the truckers profit with a trip
	anywhere in the specified range. Because the problem is NP-hard, solve aims to find
	a best solution in real time, but does not guarantee an optimal soluiton.
	"""
	def solve():

		def getHeurScore(node):
			#TODO write the heuristic
			#features
			#average number of jobs in area number of jobs nearby
			#average price of jobs nearby
			#average price of gas nearby
			#distance from home
			#time left - if not enough to get home, -infinite
			#dot_product with weights array
			#we should learn what these weights are.


		def updateBestPaths(cur_profit, cur_path):
			round_trip_cost = cur_profit - node.home.price
			if cur_days + node.home.time > self.min_days
				if abs(round_trip_cost - self.bestScore) < PROFIT_THRESHOLD: #TODO round
					if round_trip_cost > self.bestScore:
						self.bestScore = round_trip_cost
						self.bestPaths.append(list(cur_path)) #make copy of the path so far.
						self.pathScores.append([round_trip_cost])
						self.bestPaths = [self.bestPaths[i] for i in xrange(len(self.bestPaths)) \
						if abs(self.pathScores[i] - self.bestScore) < PROFIT_THRESHOLD]
					else:
						self.bestPaths.append(list(cur_path)) #make copy of the path so far.
						self.pathScores.append([round_trip_cost])

				elif round_trip_cost - self.bestScore > PROFIT_THRESHOLD:
					self.bestScore = round_trip_cost
					self.bestPaths = [list(cur_path)]
					self.pathScores = [round_trip_cost]


		def find_next_node(node, visited, cur_days, depth=0):
			if depth == FIND_NODE_DEPTH:
				node_hueristic_score = getHeurScore(node, cur_days)
				return None, node_hueristic_score
			pq = Queue.PriorityQueue() #need to keep best scores, so multiply input by -1.

			for edge in node.edges:
				if edge.nextNode
				heur_score = -1 * getHeurScore(edge.next, cur_days)

				if pq.qsize() == EXPLORE_EDGES:
					min_edge = pq.get()
					if heur_score < min_edge[0]:
						pq.put((heur_score, edge))
					else:
						pq.put(min_edge)
				else:
					pq.put((heur_score, edge))

			###At this point, we have the predicted top EXPLORE_EDGES in memory
			###TODO make this weighted by the score, so bad one steps aren't show stoppers.


			best_score = -1 * float('inf')
			best_edge = None
			while pq.qsize != 0:
				edge = pq.get()[1]
				visited.add(edge.nextNode())
				edge, score = find_next_node(edge.nextNode(), visited, cur_days + edge.time, depth+1)
				visited.remove(edge.nextNode())
				if score > best_score:
					best_score = score
					best_edge = edge

			return best_edge

			#now we have all of the interesting edges in a list.
			#now we dive deep a few layers, figuring out which one
			#accumulated the most money after a few depths.
			#once there, it runs a heuristic evaluating the value
			#of the terminal node. whichever original edge was best
			#will be returned


		def rec_solve(node, visited, cur_days, cur_profit, cur_path):
			if cur_days + node.home.time > self.max_days:
				return

			updateBestPaths(cur_profit, cur_path)

			next_edge, _ = find_next_node(node, visited, cur_days)
			visited.add(next_edge.nextNode())
			cur_path.append(node)

			rec_solve(next_node.nextNode(), visited, cur_days + next_edge.time, cur_profit + next_edge.profit, cur_path)
						

		node = self.graph.getStartNode()
		visited = set()
		cur_path = []
		rec_solve(node, visited, 0, 0, cur_path)
		return self.bestPaths, pathScores


