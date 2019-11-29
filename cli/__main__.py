import argparse
import requests

def run(args):
    operation = input("Enter GET or POST: ")

    if operation == "POST":
        print("POST")
        print(handle_post_request())
    elif operation == "GET":
        print("GET")
        print(handle_get_request())
    else:
        exit()

def get_params():
    player = input("Enter Player: ")
    match = input("Enter Match: ")

    params = {
        "player": player,
        "match": match
    }

    return params

def post_params():
    month = input("Enter Month: ")
    year = input("Enter Year: ")

    params = {
        "month": month,
        "year": year
    }

    return params

def handle_get_request():
    PARAMS = get_params()
    URL = "http://127.0.0.1:5000/matches/%s/players/%s" % (PARAMS["match"], PARAMS["player"])

    r = requests.get(URL)
    data = r.json()

    return data

def handle_post_request():
    PARAMS = post_params()
    URL = "http://127.0.0.1:5000/matches?month=%s&year=%s" % (PARAMS["month"], PARAMS["year"])

    r = requests.post(URL)
    data = r.json()

    return data

def main():
	parser=argparse.ArgumentParser(description="NBA Statistics CLI")
	parser.set_defaults(func=run)
	args=parser.parse_args()
	args.func(args)

if __name__=="__main__":
	main()