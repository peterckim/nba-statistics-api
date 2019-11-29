import flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
import urllib
from marshmallow_sqlalchemy import ModelSchema

import services.data_handling as nba_service

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


# Routes
@app.route('/', methods=['GET'])
def home():
    return "NBA Statistics API"

@app.route('/players/<int:id>', methods=['GET'])
def get_player(id):
    player = Player.query.get(id)
    player_schema = PlayerSchema()

    dump_data = player_schema.dump(player)

    return flask.jsonify(dump_data)

@app.route('/players', methods=['GET', 'POST'])
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

@app.route('/matches/<int:match_id>/players/<int:player_id>', methods=['GET'])
def get_player_match(match_id, player_id):
    player_match = PlayerMatch.query.filter(PlayerMatch.player_id == player_id).filter(PlayerMatch.match_id == match_id).first()
    player_match_schema = PlayerMatchSchema()

    dump_data = player_match_schema.dump(player_match)

    return flask.jsonify(dump_data)

@app.route('/matches/<int:id>', methods=['GET'])
def get_match(id):
    match = Match.query.get(id)
    match_schema = MatchSchema()

    dump_data = match_schema.dump(match)

    return flask.jsonify(dump_data)

@app.route('/matches', methods=['GET', 'POST'])
#HERE
def handle_matches():
    if (request.method == 'POST'):
        month = request.args.get('month')
        year = request.args.get('year')

        nba_service.add_stats_to_database(db, Player, Match, PlayerMatch, year, month)


        test = {
            "month": "october",
            "year": "2020"
        }

        # scrape website and store in the database

        # return the data

        return flask.jsonify(test)

    else:
        matches = Match.query.all()
        match_schema = MatchSchema()
        match_list = []

        for match in matches:
            match_list.append(match_schema.dump(match))

        print(flask.request)
        return flask.jsonify(match_list)




app.run()