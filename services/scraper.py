import urllib
import bs4
import re
import datetime

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
		links.append(baseURL + a.contents[0]['href'])

	return links


def obtain_players(links):
	allTables = []
	playerRows = []

	for link in links:
		uClient = uReq(link)
		page_html = uClient.read()
		uClient.close()
		page_soup = soup(page_html, "html.parser")

		for table in page_soup.find_all("table", id=re.compile("game-basic$")):
			allTables.append(table)

	for table in allTables:
		for element in table.tbody.find_all("tr", class_=lambda x: x != 'thead'):
			playerRows.append(element.th.get_text())

	return playerRows


def obtain_matches(links):
	links = obtain_match_links()
	allScoreBoxes = []

	for link in links:
		uClient = uReq(link)
		page_html = uClient.read()
		uClient.close()
		page_soup = soup(page_html, "html.parser")

		allScoreBoxes.append(page_soup.find("div", {"class": "scorebox"}))

	return allScoreBoxes


def add_stats():

	# uClient = uReq(links[0])
	# page_html = uClient.read()
	# uClient.close()
	# page_soup = soup(page_html, "html.parser")

	# for table in page_soup.find_all("table", id=re.compile("game-basic$")):
	# 	allTables.append(table)

	return links

	# for link in links:
	# 	uClient = uReq(link)
	# 	page_html = uClient.read()
	# 	uClient.close()
	# 	page_soup = soup(page_html, "html.parser")
	#
	# 	scoreBox = page_soup.find("div", {"class": "scorebox"})
	#
	# 	home_team = scoreBox.findAll("strong")[1].a.get_text()
	# 	away_team = scoreBox.findAll("strong")[0].a.get_text()
	# 	date_meta = scoreBox.find("div", {"class": "scorebox_meta"}).find("div").get_text()
	# 	date = datetime.datetime.strptime(date_meta, '%I:%M %p, %B %d, %Y')
	#
	# 	match = svc.find_match(home_team, away_team, date)
	#
	# 	for table in page_soup.find_all("table", id=re.compile("game-basic$")):
	# 		for player in table.tbody.find_all("tr", class_=lambda x: x != 'thead'):
	# 			name = player.th.get_text()
	# 			old_account = svc.find_player_by_name(name)
	# 			if old_account:
	# 				if player.find("td", {"data-stat": "reason"}):
	# 					print("Did not Play")
	# 				else:
	# 					fgm = player.find_all("td", {"data-stat": "fg"})[0].get_text()
	# 					fga = player.find_all("td", {"data-stat": "fga"})[0].get_text()
	# 					ftm = player.find_all("td", {"data-stat": "ft"})[0].get_text()
	# 					fta = player.find_all("td", {"data-stat": "fta"})[0].get_text()
	# 					fg3 = player.find_all("td", {"data-stat": "fg3"})[0].get_text()
	# 					pts = player.find_all("td", {"data-stat": "pts"})[0].get_text()
	# 					rebs = player.find_all("td", {"data-stat": "trb"})[0].get_text()
	# 					asts = player.find_all("td", {"data-stat": "ast"})[0].get_text()
	# 					stls = player.find_all("td", {"data-stat": "stl"})[0].get_text()
	# 					blks = player.find_all("td", {"data-stat": "blk"})[0].get_text()
	# 					tos = player.find_all("td", {"data-stat": "tov"})[0].get_text()
	#
	# 					svc.create_player_match(old_account.id, match.id, fgm, fga, ftm, fta, fg3, pts, rebs, asts, stls, blks, tos)
	#
	# 			else:
	# 				print("player created")
	# 				current_player = svc.create_player(name)
	# 				if player.find("td", {"data-stat": "reason"}):
	# 					print("Did not Play")
	# 				else:
	# 					fgm = player.find_all("td", {"data-stat": "fg"})[0].get_text()
	# 					fga = player.find_all("td", {"data-stat": "fga"})[0].get_text()
	# 					ftm = player.find_all("td", {"data-stat": "ft"})[0].get_text()
	# 					fta = player.find_all("td", {"data-stat": "fta"})[0].get_text()
	# 					fg3 = player.find_all("td", {"data-stat": "fg3"})[0].get_text()
	# 					pts = player.find_all("td", {"data-stat": "pts"})[0].get_text()
	# 					rebs = player.find_all("td", {"data-stat": "trb"})[0].get_text()
	# 					asts = player.find_all("td", {"data-stat": "ast"})[0].get_text()
	# 					stls = player.find_all("td", {"data-stat": "stl"})[0].get_text()
	# 					blks = player.find_all("td", {"data-stat": "blk"})[0].get_text()
	# 					tos = player.find_all("td", {"data-stat": "tov"})[0].get_text()
	#
	# 					svc.create_player_match(current_player.id, match.id, fgm, fga, ftm, fta, fg3, pts, rebs, asts, stls, blks, tos)