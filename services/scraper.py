from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

baseURL = 'https://www.basketball-reference.com'

def obtain_match_links(year, month):
	links = []
	my_url = baseURL + '/leagues/NBA_{}_games-{}.html'.format(year, month)
	uClient = uReq(my_url)
	page_html = uClient.read()
	uClient.close()
	page_soup = soup(page_html, "html.parser")

	for a in page_soup.find_all("td", {"data-stat": "box_score_text"}):
		if not len(a.contents) == 0:
			links.append(baseURL + a.contents[0]['href'])

	return links