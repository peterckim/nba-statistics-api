import services.scraper as scraper
import datetime
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re


def add_stats_to_database(db, Player, Match, PlayerMatch, year, month):
    links = scraper.obtain_match_links(year, month)

    for link in links:
        uClient = uReq(link)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")

        scoreBox = page_soup.find("div", {"class": "scorebox"})

        home_team = scoreBox.findAll("strong")[1].a.get_text()
        away_team = scoreBox.findAll("strong")[0].a.get_text()
        home_team_score = scoreBox.findAll("div", {"class": "score"})[1].get_text()
        away_team_score = scoreBox.findAll("div", {"class": "score"})[0].get_text()
        date_meta = scoreBox.find("div", {"class": "scorebox_meta"}).find("div").get_text()
        date = datetime.datetime.strptime(date_meta, '%I:%M %p, %B %d, %Y')

        match_object = Match.query.filter(Match.home_team == home_team).filter(
            Match.away_team == away_team).filter(Match.date == date).first()

        if not match_object:
            new_match = Match(home_team, away_team, home_team_score, away_team_score, date)
            db.session.add(new_match)
            db.session.commit()

        for table in page_soup.find_all("table", id=re.compile("game-basic$")):
            for player in table.tbody.find_all("tr", class_=lambda x: x != 'thead'):
                before_name = player.th.get_text()
                name = before_name.replace("č", "c").replace("ć", "c").replace("č", "c").replace("ū", "u").replace(
                    "ā", "a").replace("ņ", "n").replace("ģ", "g").replace("İ", "I").replace("Č", "C")

                player_object = Player.query.filter(Player.name == name).first()

                if not player_object:
                    new_player = Player(name)
                    db.session.add(new_player)
                    db.session.commit()

                if not player.find("td", {"data-stat": "reason"}):
                    match_object = Match.query.filter(Match.home_team == home_team).filter(
                        Match.away_team == away_team).filter(Match.date == date).first()

                    player_object = Player.query.filter(Player.name == name).first()

                    old_player_match = PlayerMatch.query.filter(PlayerMatch.player_id == player_object.id).filter(PlayerMatch.match_id == match_object.id).first()

                    if not old_player_match:
                        fgm = player.find_all("td", {"data-stat": "fg"})[0].get_text()
                        fga = player.find_all("td", {"data-stat": "fga"})[0].get_text()
                        ftm = player.find_all("td", {"data-stat": "ft"})[0].get_text()
                        fta = player.find_all("td", {"data-stat": "fta"})[0].get_text()
                        fg3 = player.find_all("td", {"data-stat": "fg3"})[0].get_text()
                        pts = player.find_all("td", {"data-stat": "pts"})[0].get_text()
                        rebs = player.find_all("td", {"data-stat": "trb"})[0].get_text()
                        asts = player.find_all("td", {"data-stat": "ast"})[0].get_text()
                        stls = player.find_all("td", {"data-stat": "stl"})[0].get_text()
                        blks = player.find_all("td", {"data-stat": "blk"})[0].get_text()
                        tos = player.find_all("td", {"data-stat": "tov"})[0].get_text()

                        new_player_match = PlayerMatch(player_object.id, match_object.id, fgm, fga, ftm, fta, fg3, pts, rebs, asts, stls, blks, tos)
                        db.session.add(new_player_match)
                        db.session.commit()
