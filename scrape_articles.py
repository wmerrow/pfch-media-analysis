import requests
from bs4 import BeautifulSoup
import json

# list of media organizations
orgs = {
	'nyt': {
		'handle': 'nytimes',
		'author_id': '807095'
	},
	'vox': {
		'handle': 'voxdotcom',
		'author_id': '2347049341'
	},
	'cnn': {
		'handle': 'cnn',
		'author_id': '759251'
	},
	'fox': {
		'handle': 'foxnews',
		'author_id': '1367531'
	},
	'oan': {
		'handle': 'oann',
		'author_id': '1209936918'
	}
}

# empty lists for storing results
articles = []
text = []

# load json file
with open("output/output__URL_True__Search_Trump.json") as f:

	tweets = json.load(f)

for org in orgs: 

	# reset org articles
	org_articles = []
	org_articles_unique = []

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

			# reset p list
			p_list = []

			if org == 'nyt':
				
				# ignore articles with "transiton highlights" in the title
				### may be better to replace this with a check for live-blog classes since seems like there are other live blogs than just transition highlights
				if 'Transition Highlights: ' not in h1:

					p_container = article_soup.find('section', {'name': 'articleBody'})
					if p_container is not None:
						p_list = p_container.findAll('p')

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


			## these types of articles currently have empty p_lists:
			# CNN - https://www.cnn.com/politics/live-news/biden-trump-us-election-news-12-02-20/index.html
			# NYT - https://www.nytimes.com/live/2020/11/30/us/joe-biden-trump
			# seems like they are updated live so probably don't want to scrape them anyway
			# also videos that have no text, which is fine
			# also special things like this NYT quiz which seems fine - The Trump Administration Just Made the Citizenship Test Harder. How Would You Do? 

			# if p list is not empty, then add URL, headline, first paragraph, and article text to org list
			if len(p_list) > 0:

				# store first paragraph
				first_p = p_list[0].text

				# combine h1 and p list into article text
				article_text = h1
				for p in p_list:
					article_text = article_text + ' ' + p.text 

				# add to org's article list along with number of tweet likes
				org_articles.append({
					'org': org,
					'article_url': article_url,
					'h1': h1,
					'first_p': first_p,
					'article_text': article_text,
					'tweet_likes': tweet['public_metrics']['like_count']
					})	


	print(len(org_articles), 'total articles')


	# filter to just those that have unique article_urls

	# empty list for compiling running list of URLs as it loops through
	existing_urls = []

	# loop through articles
	for a in org_articles:

		# if the article's URL is not already in running list of URLs, add the article to the list of unique articles and then add the URL to the running list of URLs
		if a['article_url'] not in existing_urls:
			# note - could just append a instead of writing out each key value of a, but that would include tweet likes, which we want to leave out
			org_articles_unique.append({
				'org': a['org'],
				'article_url': a['article_url'],
				'h1': a['h1'],
				'first_p': a['first_p'],
				'article_text': a['article_text']
				})
			existing_urls.append(a['article_url'])


	# aggregate number of likes for each URL (engagement)

	# for each unique URL, loop through the list of org articles and sum likes for each article with a matching article URL
	for a_u in org_articles_unique:

		# reset URL likes sum
		url_likes = 0

		# loop through non-unique org articles 
		for a_nu in org_articles:

			# if current URL is current unique URL
			if a_nu['article_url'] == a_u['article_url']:

				# add URL's engagement to running sum of unique URL's engagement
				url_likes = url_likes + a_nu['tweet_likes']

		# add summed engagement key and value to current article dict
		a_u['url_likes'] = url_likes


	# overwrite org articles with unique org articles
	org_articles = org_articles_unique
	print(len(org_articles), 'unique articles')


	# write output org articles for reference
	json.dump(org_articles, open(f'output/{org}_articles.json', 'w'), indent = 2)

	# add org list to list of all articles
	articles = articles + org_articles

	# combine article text from all of org's articles
	org_text = ''
	for a in org_articles:
		org_text = org_text + a['article_text']

	# add org name and text to text list (for processing later)
	text.append({
				'org': org,
				'org_text': org_text
				})
	print(len(text), 'dicts in text list')


print('\n\n')
print(len(articles), 'total articles')

# write output
json.dump(articles, open(f'output/articles.json', 'w'), indent = 2)
json.dump(text, open(f'output/text.json', 'w'), indent = 2)

