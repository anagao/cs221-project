
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
	EXPLORE_EDGES = 15
	FIND_NODE_DEPTH = 3

	def __init__(self, graph, start_lat, start_lng, min_days, max_days):
		# Graph data structure
		self.graph = graph

		# user-defined parameters to algorithm
		self.max_days = max_days
				
		# algorithm data structures
		self.start_job_id = graph.create_start_node(start_lat, start_lng) # create pseudo-start node
		self.end_job_id = self.start_job_id

	"""
	solve
	A wrapper function that attempts to find the best path for to maximize the truckers profit with a trip
	anywhere in the specified range. Because the problem is NP-hard, solve aims to find
	a best solution in real time, but does not guarantee an optimal soluiton.
	"""
	def solve(self):

		def find_next_node(node_id, visited, cur_days, depth=0):
			"""
			Given we are currently at <node_id>, find the next job we should assign,
			and return next_node_id, job_days, job_money, return_home_cost

			@param <String> node_id
			"""

			visited.add(node_id)
			pq = Queue.PriorityQueue()
			neighbor_dict = self.graph.distances_from(node_id)
			for neighbor_id in neighbor_dict:
				interjob_distance, intrajob_distance = neighbor_dict[neighbor_id]
				# avoid visiting a job twice
				if neighbor_id in visited: continue

				total_dist_to_home = interjob_distance + intrajob_distance + self.graph.get_distance(neighbor_id, self.end_job_id)
				min_days_to_home = util.miles_to_drive_days(total_dist_to_home)
				if cur_days + min_days_to_home > self.max_days: continue #don't consider if it forces not to get home on time.
				
				# need to keep best scores, so multiply input by -1
				price = self.graph.get_price(neighbor_id)

				trip_days = util.miles_to_drive_days( interjob_distance+intrajob_distance )
				score = -1 * util.compute_profit(price, interjob_distance, intrajob_distance) / trip_days
				if pq.qsize() == BestRoute.EXPLORE_EDGES:
					min_edge = pq.get()
					if score < min_edge[0]:
						pq.put((score, (neighbor_id, interjob_distance, intrajob_distance, price)))
					else:
						pq.put(min_edge)
				else:
					pq.put((score, (neighbor_id, interjob_distance, intrajob_distance, price)))

			###At this point, we have the predicted top EXPLORE_EDGES in memory
			best_score = -1 * float('inf')
			best_next_node_id = -1
			best_job_days = None
			best_jobs_money = None
			best_return_home_cost = None

			while pq.qsize() != 0:
				neg_one_step_profit, neighbor_tuple = pq.get()
				neighbor_id, interjob_distance, intrajob_distance, price = neighbor_tuple
				one_step_profit = -1 * neg_one_step_profit
				#print("one step prof: " + str(one_step_profit))
				additional_days = util.miles_to_drive_days(interjob_distance + intrajob_distance)

				if depth == BestRoute.FIND_NODE_DEPTH - 1: #limit the search
					next_score = self.evaluation_function(neighbor_id, cur_days + additional_days)
				else:
					next_node_id, job_days, job_money, return_home_cost, next_score = find_next_node(neighbor_id, visited, cur_days + additional_days, depth+1)

				if one_step_profit +  next_score > best_score:
					best_score = one_step_profit + next_score
					best_next_node_id = neighbor_id
					best_job_days = additional_days
					best_jobs_money = util.compute_profit(price, interjob_distance, intrajob_distance)
					best_return_home_cost = self.graph.get_distance(neighbor_id, self.end_job_id) * util.EMPTY_DOLLAR_PER_MILE

			if depth != 0: visited.remove(node_id)
			return best_next_node_id, best_job_days, best_jobs_money, best_return_home_cost, best_score

			#now we have all of the interesting edges in a list.
			#now we dive deep a few layers, figuring out which one
			#accumulated the most money after a few depths.
			#once there, it runs a heuristic evaluating the value
			#of the terminal node. whichever original edge was best
			#will be returned



		def rec_solve(node_id, visited, cur_days, cur_profit, cur_path, path_profit):
			"""
			@param <String> node_id = id of a job
			"""

			next_node_id, job_days, job_money, return_home_cost, _ = find_next_node(node_id, visited, cur_days)


			if next_node_id != -1: #a valid next job exists
				cur_path.append(next_node_id)
				path_profit.append(cur_profit + job_money - return_home_cost)
				visited.add(next_node_id)
				print("made step")
				print(job_days)
				print(len(visited))
				rec_solve(next_node_id, visited, cur_days + job_days, cur_profit + job_money, cur_path, path_profit)



		visited = set()
		visited.add(self.start_job_id)
		cur_path = []
		path_profit = []
		rec_solve(self.start_job_id, visited, 0, 0, cur_path, path_profit)
		#todo return best path of the array.
		print(cur_path)
		print(path_profit)
		return path_profit

	def evaluation_function(self, node_id, cur_days):
		"""
		Evaluation function: if I add node_id to the job schedule, how good is it?
		@author Aaron Nagao

		@param <String> node_id = id of the job I am evaluating
		@return <float> estimate of the value of choosing node_id. Higher value = better choice.

		TODO: change manual weights of 1 to learned weights

		Features for evaluation function:
		# 1) Number of miles required to fulfill this job
		# 2) price of this job
		# 3a) After we deliver this job, how many other jobs are in the area?
		# 3b) After we deliver this job, what's the average price of other jobs in the delivery area?
		# TODO: avg gas price in the area?
		"""
		# key: <String>featureName => value: <tuple>(weight, featureValue)
		# Positive weights for good features.
		features = dict()

		"""
		# First, check whether I can finish this job in time
		prevEnd_nextStart_nextEnd = self.distance_matrix[(prevJob['_id']['$oid'], nextJob['_id']['$oid'])] # miles required to drive to next job and fulfill next job (prevJob.end => nextJob.start => nextJob.end)
		
		(from_lng, from_lat) = nextJob['deliveryAddress']['location']['coordinates']
  		(to_lng, to_lat) = (self.start_lng, self.start_lat)
		nextEnd_home = util.distance(from_lat, from_lng, to_lat, to_lng)
		
		sumDays_nextJobAndHome = ( (prevEnd_nextStart_nextEnd + nextEnd_home) / util.MPH ) / 24 # day = miles / miles/hr / 24hr/day
		if cur_days + sumDays_nextJobAndHome > self.max_days:
			return float('-inf') # cannot take on this job
		"""
		
		# 1) Number of miles required to fulfill this job
		# negative weight (prefer shorter jobs)
		features['jobMiles'] = (-.2, util.distance(*self.graph.jobs[node_id]['pickup']+self.graph.jobs[node_id]['delivery']))

		# 2) price of this job
		features['jobPrice'] = (0.3, self.graph.jobs[node_id]['price'])
		
		# 3a) After we deliver this job, how many other jobs are in the area?
		(to_lat, to_lng) = self.graph.jobs[node_id]['delivery']
		to_i, to_j = int(to_lat), int(to_lng)  
		jobsInDeliveryArea = self.graph.delivery_grid[ (to_i, to_j) ]
		numJobsInDeliveryArea = len(jobsInDeliveryArea)
		features['numJobsInDeliveryArea'] = (0.3, numJobsInDeliveryArea)

		# 3b) After we deliver nextJob, what's the average price of other jobs in the delivery area?
		if numJobsInDeliveryArea == 0:
			avgPriceInDeliveryArea = 0
		else:
			avgPriceInDeliveryArea = sum([self.graph.get_price(job) for job in jobsInDeliveryArea]) / numJobsInDeliveryArea
		features['avgPriceInDeliveryArea'] = (0.1, avgPriceInDeliveryArea)
		
		# print features
		heur_score = sum([ v[0]*v[1] for k,v in features.iteritems() ]) / 100
		#print("heur score: " + str(heur_score))
		return heur_score # dot product of feature and its weight


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
