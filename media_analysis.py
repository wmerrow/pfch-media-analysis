import requests
import json

# get api keys from json file (in gitignore)
with open("keys.json") as f:
    keys = json.load(f)

btoken = keys['bearer_token']

url = 'https://api.twitter.com/2/tweets/search/recent'

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

#for org_id in orgs:
#	print(orgs[org_id]['handle'])
#	print(orgs[org_id]['url'])


# define as None initially
next_token = None
all_data = []

# make requests and combine responses into one json file until there is no next token or it reaches 10 requests
for number in range(1,11):

	payload = {
		'query': 'from:nytimes url:"https://www.nytimes.com/"', 
		'tweet.fields': 'id,created_at,public_metrics,text,entities',
		'max_results': 100,
		'next_token': next_token
	}

	r = requests.get(url, params = payload, headers = headers)
	
	print('Response #', number, ': ', r.status_code, sep='')

	data = json.loads(r.text)

	# add new response to all_data, including data but not meta
	all_data = all_data + data['data']

	# if response contains a next token
	if 'next_token' in data['meta']:

		# store new next_token
		next_token = data['meta']['next_token']

	# if response does not contain next token
	else:

		print('Response #', number, ' does not have next_token', sep='')

		# end loop
		break

# filter to desired fields
#data = 

# write output as json file
json.dump(all_data, open('output.json', 'w'), indent = 2)
