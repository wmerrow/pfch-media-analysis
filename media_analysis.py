import requests
import json

# get api keys from json file (in gitignore)
with open("keys.json") as f:
    keys = json.load(f)

btoken = keys['bearer_token']

url = 'https://api.twitter.com/2/tweets/search/recent'

headers = {'Authorization': f'Bearer {btoken}'}

# list of orgs
#orgs = ['nytimes', '', '', '', '']

# for...

payload = {
	'query': 'from:nytimes url:"https://www.nytimes.com/" Michigan', 
	#'media.fields': 'url'
}

r = requests.get(url, params = payload, headers = headers)

print(r.status_code)

data = json.loads(r.text)

json.dump(data, open('output.json', 'w'), indent = 2)
