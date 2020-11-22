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

## all_data overwriting each time

# search terms
search_text = 'Michigan'

# for each organization
for org_id in orgs:

	handle = orgs[org_id]['handle']
	url = orgs[org_id]['url']

	print('\n', org_id, sep='')

	# define as empty initially
	next_token = None
	all_data = []

	# make requests, using next_token to combine multiple responses into one json file until there is no next token or 10 requests have been made

	iterations = 4

	for i in range(1, iterations + 1):

		payload = {
			# get tweets by the organization, containing the organization's URL, containing the search words
			'query': f'from:{handle} url:"{url}" {search_text}', 
			# return these fields
			'tweet.fields': 'author_id,id,created_at,public_metrics,text,entities',
			# number of results per request (can be 10-100)
			'max_results': 10,
			# specify next_token (page to start on)
			'next_token': next_token
		}

		r = requests.get(endpoint_url, params = payload, headers = headers)
		
		print('Response ', i, ': ', r.status_code, sep='')

		data = json.loads(r.text)

		print(data['meta']['result_count'], 'results')

		# if there are more than zero results, add results to all_data
		if data['meta']['result_count'] > 0:

			# add new results to all_data, including data but not meta
			all_data = all_data + data['data']

		# if response contains a next token
		if 'next_token' in data['meta']:

			# store new next_token
			next_token = data['meta']['next_token']

			# if it's the final iteration, print a warning about uncaught results
			if i == iterations:

				print('Uncaught results (final iteration has next_token)')

		# if response does not contain next token
		else:

			print('No more results (response #', i, ' does not have next_token)', sep='')

			# end loop
			break

# filter to desired fields
#data = 

# write output as json file
json.dump(all_data, open('output.json', 'w'), indent = 2)
