import requests
from bs4 import BeautifulSoup
import json

# list of media organizations
orgs = {
	# 'nyt': {
	# 	'handle': 'nytimes',
	# 	'url': 'https://www.nytimes.com/',
	# 	'author_id': '807095',
	# 	'div_class': 'StoryBodyCompanionColumn'
	# },
	# 'vox': {
	# 	'handle': 'voxdotcom',
	# 	'url': 'https://www.vox.com/',
	# 	'author_id': '2347049341',
	# 	'div_class': 'c-entry-content'
	# },
	# 'cnn': {
	# 	'handle': 'cnn',
	# 	'url': 'https://www.cnn.com/',
	# 	'author_id': '759251',
	# 	'div_class': 'l-container'
	# },
	# 'fox': {
	# 	'handle': 'foxnews',
	# 	'url': 'https://www.foxnews.com/',
	# 	'author_id': '1367531',
	# 	'div_class': 'article-body'
	# },
	'oan': {
		'handle': 'oann',
		'url': 'https://www.oann.com/',
		'author_id': '1209936918',
		'div_class': 'entry-content'
	}
}

# load json file
with open("output/output__URL_True__Search_Trump.json") as f:

	tweets = json.load(f)

nyt_counter = 0
nyt_url_counter = 0

vox_counter = 0
vox_url_counter = 0

for org in orgs:

	# reset counters
	counter = 0
	url_counter = 0

	# print org name
	print(f'\n\n{org}\n')

	# loop through tweets
	for tweet in tweets:

		# just work with tweets for the org that it's on
		if tweet['author_id'] == orgs[org]['author_id']:

			counter += 1

			# if there is a urls attribute
			if 'urls' in tweet['entities']:

				url_counter += 1

				# get url ([0] assumes there will only ever be one url in the urls array)
				article_url = tweet['entities']['urls'][0]['expanded_url']

				# get article page html and parse
				article_r = requests.get(article_url)
				article_soup = BeautifulSoup(article_r.text, features="html.parser")

				# get title
				# assumes all orgs' pages have a title and it's the first h1 on the page
				h1_list = article_soup.find_all('h1')
				h1 = h1_list[0].text
				print(h1)

				# get p tags

				if org == 'nyt':

					p_container = article_soup.find('div', {'class': 'StoryBodyCompanionColumn'})
					p = p_container.find('p').text

				elif org == 'vox':

					p_container = article_soup.find('div', {'class': 'c-entry-content'})
					p = p_container.find('p').text
				
				elif org == 'cnn':
					
					p_container = article_soup.find('section', {'id': 'body-text'})
					p = p_container.find('p').text

				elif org == 'fox':

					p_container = article_soup.find('div', {'class': 'article-body'})
					p = p_container.findChild('p', recursive=False).text  # recursive false specifies only direct children

				elif org == 'oan':

					p_container = article_soup.find('div', {'class': 'entry-content'})
					p_el = p_container.findChild('p', recursive=False)
					# handle cases when there are no p elements
					if p_el is None:
						p = ''
					else:
						p = p_el.text  # recursive false specifies only direct children


				print(p)
				print('\n')


				# write org name
				# write URL
				# write h1
				# write p

	# print results for each org
	print(str(counter) + ' tweets')
	print(str(url_counter) + ' tweets with urls')