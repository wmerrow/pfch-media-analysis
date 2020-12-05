import requests
import json

# get api keys from json file (in gitignore)
with open("keys.json") as f:
    keys = json.load(f)

btoken = keys['bearer_token']

endpoint_url = 'https://api.twitter.com/2/tweets/search/recent'

headers = {'Authorization': f'Bearer {btoken}'}

# list of media organizations
orgs = {
	'nyt': {
		'handle': 'nytimes',
		'url': 'https://www.nytimes.com/'
	},
	'vox': {
		'handle': 'voxdotcom',
		'url': 'https://www.vox.com/'
	},
	'cnn': {
		'handle': 'cnn',
		'url': 'https://www.cnn.com/'
	},
	'fox': {
		'handle': 'foxnews',
		'url': 'https://www.foxnews.com/'
	},
	'oan': {
		'handle': 'oann',
		'url': 'https://www.oann.com/'
	}
}

# function for getting tweets, specifying with or without org URL and search text
def get_tweets(has_org_url, search_text):

	# print function inputs for reference
	print('\n\nget tweets\nurl: ' + str(has_org_url) + '\nsearch text: ' + search_text)

	# empty variable for storing results
	all_data = []

	# for each organization
	for org_id in orgs:

		# print org name
		print('\n', org_id, sep='')

		# define next_token as empty initially for each org - will be overwritten below if it isn't the first loop through
		next_token = None

		# reset result count for each org
		result_count = 0

		# create parameters for query string (tweets by the organization, containing the organization's URL if specified, containing the specified search words)

		# twitter handle parameter
		handle = orgs[org_id]['handle']
		handle_param = f'from:{handle}'

		# url parameter (if true was specified in function)
		url = orgs[org_id]['url']
		if has_org_url == False:
			url_param = ''
		else:
			url_param = f' url:"{url}"'
		
		# search text
		if search_text == None:
			search_text_param = ''
		else:
			search_text_param = f' {search_text}'

		# create query string
		query = handle_param + url_param + search_text_param

		# make requests, using next_token to combine multiple responses into one json file until there is no next token or max_results number of requests have been made

		# limit iterations to avoid hitting hitting request limit
		iterations = 4

		for i in range(1, iterations + 1):

			payload = {
				# query
				'query': query,
				# include these fields in response
				'tweet.fields': 'author_id,id,created_at,public_metrics,text,entities',
				# number of results per response (can be 10-100)
				'max_results': 100,
				# specify next_token (page to start on)
				'next_token': next_token
			}

			# make request
			r = requests.get(endpoint_url, params = payload, headers = headers)
			
			# print request status
			print('Response ', i, ': ', r.status_code, sep='')

			# store page of responses
			page_data = json.loads(r.text)

			# add to result count
			result_count = result_count + page_data['meta']['result_count']

			# if there are more than zero results
			if page_data['meta']['result_count'] > 0:

				# add new results to all_data, including data but not meta
				all_data = all_data + page_data['data']

			# if response contains a next token
			if 'next_token' in page_data['meta']:

				# store new next_token
				next_token = page_data['meta']['next_token']

				# and if it's the final iteration
				if i == iterations:

					# print number of results
					print(result_count, 'results')

					# print warning about uncaught results
					print('WARNING: Uncaught results (final iteration has next_token)')

			# if response does not contain next token
			else:

				# print number of results
				print(result_count, 'results')

				# print "no more results"
				print('No more results (response ', i, ' does not have next_token)', sep='')

				# end loop
				break

	# filter to desired fields
	#data = 

	# write output of get_tweets() as json file
	json.dump(all_data, open(f'output/output__URL_{has_org_url}__Search_{search_text}.json', 'w'), indent = 2)


# get tweets 
get_tweets(has_org_url = True, search_text = 'Georgia')
get_tweets(has_org_url = False, search_text = 'Georgia')
get_tweets(has_org_url = True, search_text = 'Trump')
