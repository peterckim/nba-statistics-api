import flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
import urllib
from marshmallow_sqlalchemy import ModelSchema
from marshmallow_sqlalchemy.fields import Nested

import services.scraper as scraper
import datetime
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re

# import services.data_handling as nba_service

app = flask.Flask(__name__)
params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=nba-stats.database.windows.net;DATABASE=nba-stats;UID=peter-admin;PWD=NbaStats123")
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
db = SQLAlchemy(app)
app.config["DEBUG"] = True

# Models
class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Player(id=%r)>' % self.id

class PlayerSchema(ModelSchema):
    class Meta:
        model = Player

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String(80), nullable=False)
    away_team = db.Column(db.String(80), nullable=False)
    home_team_score = db.Column(db.Integer, primary_key=False)
    away_team_score = db.Column(db.Integer, primary_key=False)
    date = db.Column(db.DateTime, primary_key=False)

    def __init__(self, home_team, away_team, home_team_score, away_team_score, date):
        self.home_team = home_team
        self.away_team = away_team
        self.home_team_score = home_team_score
        self.away_team_score = away_team_score
        self.date = date
        
    def __repr__(self):
        return '<Match(id=%r)>' % self.id

class MatchSchema(ModelSchema):
    class Meta:
        model = Match


class Season(db.Model):
    __tablename__ = 'seasons'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)

    def __init__(self, year):
        self.year = year

    def __repr__(self):
        return '<Season(id=%r)>' % self.id


class SeasonSchema(ModelSchema):
    class Meta:
        model = Season

class PlayerMatch(db.Model):
    __tablename__ = 'player_matches'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))

    field_goals_made = db.Column(db.Integer, nullable=False)
    field_goals_attempted = db.Column(db.Integer, nullable=False)
    free_throws_made = db.Column(db.Integer, nullable=False)
    free_throws_attempted = db.Column(db.Integer, nullable=False)
    three_pointers_made = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    rebounds = db.Column(db.Integer, nullable=False)
    assists = db.Column(db.Integer, nullable=False)
    steals = db.Column(db.Integer, nullable=False)
    blocks = db.Column(db.Integer, nullable=False)
    turnovers = db.Column(db.Integer, nullable=False)

    def __init__(self, player_id, match_id, field_goals_made, field_goals_attempted, free_throws_made, free_throws_attempted, three_pointers_made, points, rebounds, assists, steals, blocks, turnovers):
        self.player_id = player_id
        self.match_id = match_id
        self.field_goals_made = field_goals_made
        self.field_goals_attempted = field_goals_attempted
        self.free_throws_made = free_throws_made
        self.free_throws_attempted = free_throws_attempted
        self.three_pointers_made = three_pointers_made
        self.points = points
        self.rebounds = rebounds
        self.assists = assists
        self.steals = steals
        self.blocks = blocks
        self.turnovers = turnovers

    def __repr__(self):
        return '<PlayerMatch(id=%r)>' % self.id

class PlayerMatchSchema(ModelSchema):
    class Meta:
        model = PlayerMatch

class PlayerSeason(db.Model):
    __tablename__ = 'player_seasons'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id'))
    player = db.relationship(Player, backref='player_seasons')

    field_goals_made = db.Column(db.DECIMAL(asdecimal=False), nullable=False)
    field_goals_attempted = db.Column(db.DECIMAL(asdecimal=False), nullable=False)
    free_throws_made = db.Column(db.DECIMAL(asdecimal=False), nullable=False)
    free_throws_attempted = db.Column(db.DECIMAL(asdecimal=False), nullable=False)
    three_pointers_per_game = db.Column(db.DECIMAL(asdecimal=False), nullable=False)
    points_per_game = db.Column(db.DECIMAL(asdecimal=False), nullable=False)
    rebounds_per_game = db.Column(db.DECIMAL(asdecimal=False), nullable=False)
    assists_per_game = db.Column(db.DECIMAL(asdecimal=False), nullable=False)
    steals_per_game = db.Column(db.DECIMAL(asdecimal=False), nullable=False)
    blocks_per_game = db.Column(db.DECIMAL(asdecimal=False), nullable=False)
    turnovers_per_game = db.Column(db.DECIMAL(asdecimal=False), nullable=False)



    def __init__(self, player_id, season_id, field_goals_made, field_goals_attempted, free_throws_made, free_throws_attempted, three_pointers_per_game, points_per_game, rebounds_per_game, assists_per_game, steals_per_game, blocks_per_game, turnovers_per_game):
        self.player_id = player_id
        self.season_id = season_id
        self.field_goals_made = field_goals_made
        self.field_goals_attempted = field_goals_attempted
        self.free_throws_made = free_throws_made
        self.free_throws_attempted = free_throws_attempted
        self.three_pointers_per_game = three_pointers_per_game
        self.points_per_game = points_per_game
        self.rebounds_per_game = rebounds_per_game
        self.assists_per_game = assists_per_game
        self.steals_per_game = steals_per_game
        self.blocks_per_game = blocks_per_game
        self.turnovers_per_game = turnovers_per_game

    def __repr__(self):
        return '<PlayerSeason(id=%r)>' % self.id


class SmartNested(Nested):
    def serialize(self, attr, obj, accessor=None):
        if attr not in obj.__dict__:
            return {"id": int(getattr(obj, attr + "_id"))}
        return super(SmartNested, self).serialize(attr, obj, accessor)


class PlayerSeasonSchema(ModelSchema):
    player = SmartNested(PlayerSchema)
    class Meta:
        model = PlayerSeason


# Routes
@app.route('/api', methods=['GET'])
def home():
    return "NBA Statistics API"

@app.route('/api/players/<int:id>', methods=['GET'])
def get_player(id):
    player = Player.query.get(id)
    player_schema = PlayerSchema()

    dump_data = player_schema.dump(player)

    return flask.jsonify(dump_data)

@app.route('/api/players', methods=['GET', 'POST'])
def handle_players():
    if (flask.request == 'POST'):
        #Post a new player
        print('post a new player')
    else:
        players = Player.query.all()
        player_schema = PlayerSchema()
        player_list = []

        for player in players:
            player_list.append(player_schema.dump(player))

        return flask.jsonify(player_list)

@app.route('/api/matches/<int:match_id>/players/<int:player_id>', methods=['GET'])
def get_player_match(match_id, player_id):
    player_match = PlayerMatch.query.filter(PlayerMatch.player_id == player_id).filter(PlayerMatch.match_id == match_id).first()
    player_match_schema = PlayerMatchSchema()

    dump_data = player_match_schema.dump(player_match)

    return flask.jsonify(dump_data)

@app.route('/api/matches/<int:id>', methods=['GET'])
def get_match(id):
    match = Match.query.get(id)
    match_schema = MatchSchema()

    dump_data = match_schema.dump(match)

    return flask.jsonify(dump_data)

@app.route('/api/matches', methods=['GET', 'POST'])
#HERE
def handle_matches():
    if (request.method == 'POST'):
        month = request.args.get('month')
        year = request.args.get('year')

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

                        old_player_match = PlayerMatch.query.filter(PlayerMatch.player_id == player_object.id).filter(
                            PlayerMatch.match_id == match_object.id).first()

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

                            new_player_match = PlayerMatch(player_object.id, match_object.id, fgm, fga, ftm, fta, fg3,
                                                           pts, rebs, asts, stls, blks, tos)
                            db.session.add(new_player_match)
                            db.session.commit()

        # nba_service.add_stats_to_database(db, Player, Match, PlayerMatch, year, month)

        test = {
            "month": "october",
            "year": "2020"
        }

        return flask.jsonify(test)

    else:
        matches = Match.query.all()
        match_schema = MatchSchema()
        match_list = []

        for match in matches:
            match_list.append(match_schema.dump(match))

        print(flask.request)
        return flask.jsonify(match_list)

@app.route('/api/seasons/<int:season_id>/players/<int:player_id>', methods=['GET'])
def get_player_season(season_id, player_id):
    player_season = PlayerSeason.query.filter(PlayerSeason.player_id == player_id).filter(PlayerSeason.season_id == season_id).first()
    player_season_schema = PlayerSeasonSchema()

    dump_data = player_season_schema.dump(player_season)

    return flask.jsonify(dump_data)


@app.route('/api/seasons/<int:season_id>/players', methods=['GET'])
def get_players_season(season_id):
    player_seasons = PlayerSeason.query.join(Player).filter(PlayerSeason.season_id == season_id)
    # player_seasons = PlayerSeason.query.filter(PlayerSeason.season_id == season_id)
    player_season_schema = PlayerSeasonSchema()
    player_seasons_list = []

    for player_season in player_seasons:
        print(player_season.player)
        # print((player_season_schema.dump(player_season)))
        player_seasons_list.append(player_season_schema.dump(player_season))



    return flask.jsonify(player_seasons_list)


app.run()