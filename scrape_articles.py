import requests
from bs4 import BeautifulSoup
import json

# list of media organizations
orgs = {
	'nyt': {
		'handle': 'nytimes',
		'url': 'https://www.nytimes.com/',
		'author_id': '807095'
	},
	'vox': {
		'handle': 'voxdotcom',
		'url': 'https://www.vox.com/',
		'author_id': '2347049341'
	},
	'cnn': {
		'handle': 'cnn',
		'url': 'https://www.cnn.com/',
		'author_id': '759251'
	},
	'fox': {
		'handle': 'foxnews',
		'url': 'https://www.foxnews.com/',
		'author_id': '1367531'
	},
	'oan': {
		'handle': 'oann',
		'url': 'https://www.oann.com/',
		'author_id': '1209936918'
	}
}

# empty list for storing results
articles = []

# load json file
with open("output/output__URL_True__Search_Trump.json") as f:

	tweets = json.load(f)

for org in orgs: 

	# reset org articles
	org_articles = []

	# filter to just tweets by the current org
	org_tweets = [d for d in tweets if d['author_id'] == orgs[org]['author_id']]

	# print org name
	print(f'\n\n{org}')

	# loop through the org's tweets, going to each tweet URL and scraping the article text
	for tweet in org_tweets:

		# if there is a urls attribute
		if 'urls' in tweet['entities']:

			# URL in tweet ([0] assumes there will only ever be one url in the urls array)
			tweet_url = tweet['entities']['urls'][0]['expanded_url']

			# make request and store response
			article_response = requests.get(tweet_url)

			# store article URL (since tweet URLs are usually shortened URLs and multiple redirect to the same end URL)
			article_url = article_response.url

			# article page html
			article_soup = BeautifulSoup(article_response.text, features="html.parser")

			# store headline (assumes all orgs' pages have a title and it's the first h1 on the page)
			h1_list = article_soup.find_all('h1')
			h1 = h1_list[0].text

			# store list of p tags, using the appropriate scraping approach depending on the org

			if org == 'nyt':
				
				# ignore articles with "transiton highlights" in the title
				### may be better to replace this with a check for live-blog classes since seems like there are other live blogs than just transition highlights
				if 'Transition Highlights: ' not in h1:

					p_container = article_soup.find('section', {'name': 'articleBody'})
					if p_container is not None:
						p_list = p_container.findAll('p')
						#p = p_list[0].text

				##### need to reset p stuff each time so that it doesn't use p stuff from previous one in cases like transition highlights

			elif org == 'vox':

				# some articles have empty p tags at start, not a problem
				p_container = article_soup.find('div', {'class': 'c-entry-content'})
				if p_container is not None:
					p_list = p_container.findChildren('p', recursive=False) # recursive false specifies only direct children
			
			elif org == 'cnn':

				# could remove p tags with class zn-body__footer ("x y z contributed to this report...")
				p_container = article_soup.find('section', {'id': 'body-text'})
				if p_container is not None:
					p_list = p_container.findAll('p')

			elif org == 'fox':

				p_container = article_soup.find('div', {'class': 'article-body'})
				if p_container is not None:
					p_list = p_container.findChildren('p', recursive=False) # recursive false specifies only direct children

			elif org == 'oan':

				p_container = article_soup.find('div', {'class': 'entry-content'})
				if p_container is not None:
					p_list = p_container.findChildren('p', recursive=False) # recursive false specifies only direct children


			# if p list is not empty, add URL, headline, first paragraph, and article text to org list
			if len(p_list) > 0:

				# store first paragraph
				first_p = p_list[0].text

				# combine h1 and p list into article text
				article_text = h1
				for p in p_list:
					article_text = article_text + ' ' + p.text 

				# add to org's article list
				org_articles.append({
					'org': org,
					'article_url': article_url,
					'h1': h1,
					'first_p': first_p,
					'article_text': article_text
					})	


	print(len(org_articles), 'articles')
	# write org output for reference
	json.dump(org_articles, open(f'output/{org}_articles.json', 'w'), indent = 2)

	# add org list to list of all articles
	articles = articles + org_articles
	#articles.append(org_list)

# filter master list to unique article_urls

print('\n\n')
print(len(articles), 'total articles')

# write output
json.dump(articles, open(f'output/articles.json', 'w'), indent = 2)

