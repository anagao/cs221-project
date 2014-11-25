from __future__ import division
import Queue
import util

"""
BestRoute is a class that expects 
Input:
	Graph: A graph with the following properties:
		We require that once a truck picks up a load, it must drop it off
		before picking up another load. Thus, we can think of a full path as
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

	Min_days: The minimum number of days that a trip can last.
	Max_days: The maximum number of days that a trip can last / total number of days that the algorithm is creating a schedule for
	Start_latitude: the latitude of the starting location for the truck
	Start_longitude: the longitude of the starting locaiton for the truck
	NOTE: we assume truck must start and end at same location! (truck goes on a tour/cycle)

"""
class BestRoute(object):
	PROFIT_THRESHOLD = 100
	EXPLORE_EDGES = 100
	FIND_NODE_DEPTH = 4

	def __init__(self, graph, distance_matrix, delivery_grid, 
				start_lat, start_lng, min_days, max_days):
		self.graph = graph
		self.distance_matrix = distance_matrix
		self.delivery_grid = delivery_grid
		self.start_lat, self.start_lng = start_lat, start_lng # heuristic assumes start location == end location!
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
	def solve(self):

		def updateBestPaths(cur_profit, cur_path):
			round_trip_cost = cur_profit - node.home.price
			if cur_days + node.home.time > self.min_days:
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
				node_hueristic_score = self.evaluation_function(prevJob, nextJob, cur_days)
				return None, node_hueristic_score
			pq = Queue.PriorityQueue()

			for edge in node.edges:
				if edge.nextNode:
					heur_score = -1 * self.evaluation_function(prevJob, nextJob, cur_days)  # need to keep best scores, so multiply input by -1

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
						

		node = self.graph.getStartNode() # TODO: change to start with nodes around self.start_lat and self.start_lng
		visited = set()
		cur_path = []
		rec_solve(node, visited, 0, 0, cur_path)
		return self.bestPaths, pathScores

	def evaluation_function(self, prevJob, nextJob, cur_days):
		"""
		Evaluation function, used in depth-limited search
		@author Aaron Nagao

		@param <dict> prevJob: the job I was just at
		@param <dict> nextJob: the job I am considering choosing
		@param <float> cur_days: the current number of days I have fulfilled, up to and including delivering prevJob (but NOT including driving from prevJob to nextJob, or fulfilling nextJob)

		@return <float> estimate of the value of choosing nextJob. Higher value = better choice.

		TODO: change manual weights of 1 to learned weights

		Features for evaluation function:
		# 1) Number of miles required to drive to next job and fulfill next job
		# 2) price of this job
		# 3a) After we deliver nextJob, how many other jobs are in the area?
		# 3b) After we deliver nextJob, what's the average price of other jobs in the delivery area?
		# TODO: avg gas price in the area?
		"""
		# key: <String>featureName => value: <tuple>(weight, featureValue)
		# Positive weights for good features.
		features = dict()

		# First, check whether I can finish this job in time
		prevEnd_nextStart_nextEnd = self.distance_matrix[(prevJob['_id']['$oid'], nextJob['_id']['$oid'])] # miles required to drive to next job and fulfill next job (prevJob.end => nextJob.start => nextJob.end)
		
		(from_lng, from_lat) = nextJob['deliveryAddress']['location']['coordinates']
  		(to_lng, to_lat) = (self.start_lng, self.start_lat)
		nextEnd_home = util.distance(from_lat, from_lng, to_lat, to_lng)
		
		sumDays_nextJobAndHome = ( (prevEnd_nextStart_nextEnd + nextEnd_home) / util.MPH ) / 24 # day = miles / miles/hr / 24hr/day
		if cur_days + sumDays_nextJobAndHome > self.max_days:
			return float('-inf') # cannot take on this job
		
		# 1) Number of miles required to drive to next job and fulfill next job
		features['jobMiles'] = (-1, prevEnd_nextStart_nextEnd) # negative weight (prefer shorter jobs)

		# 2) price of this job
		features['jobPrice'] = (1, nextJob['price'])
		
		# 3a) After we deliver nextJob, how many other jobs are in the area?
		(to_lng, to_lat) = nextJob['deliveryAddress']['location']['coordinates']
		to_i, to_j = int(to_lat), int(to_lng)  
		jobsInDeliveryArea = self.delivery_grid[ (to_i, to_j) ]
		numJobsInDeliveryArea = len(jobsInDeliveryArea)
		features['numJobsInDeliveryArea'] = (1, numJobsInDeliveryArea)

		# 3b) After we deliver nextJob, what's the average price of other jobs in the delivery area?
		if numJobsInDeliveryArea == 0:
			avgPriceInDeliveryArea = 0
		else:
			avgPriceInDeliveryArea = sum([job['price'] for job in jobsInDeliveryArea]) / numJobsInDeliveryArea
		features['avgPriceInDeliveryArea'] = (1, avgPriceInDeliveryArea)
		
		#print features
		return sum([ v[0]*v[1] for k,v in features.iteritems() ]) # dot product of feature and its weight


def testEvaluationFunction():
	# code for testing evaluation_function()
	import json, os
	JOBS_WEEK = os.path.join('project_data', 'jobs_week_2014-09-26.json')
	prevJob, nextJob = None, None
	with open(JOBS_WEEK) as f:
		for i, line in enumerate(f):
			if i==0:
				prevJob = json.loads(line)
			elif i==1:
				nextJob = json.loads(line)
			else:
				break
	cur_days = 1
	# call BestRoute.evaluation_function(prevJob, nextJob, cur_days)