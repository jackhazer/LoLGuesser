import requests
import json
import urllib.parse
import time
import csv
import random
import os
from cs50 import SQL

db = SQL("sqlite:///lolguesser.db")


class Data:
    def __init__(self):
        self.timing = 0
        self.API_KEY = 'RGAPI-0bd95d20-6ad3-46bd-9548-1bf6bdb4946a'
        self.API_URL = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/'
        self.GAME_URL = 'https://kr.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/'
        self.MATCH_URL = 'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/'
        self.MATCH_DETAIL_URL = 'https://asia.api.riotgames.com/lol/match/v5/matches/'
        self.Matches = []
        self.PLAYER_ID = ''
        self.puuid = ''
        self.puuidset = set()
        self.puuids = []
        self.idx = 1

    def add_json(self, match):
        temp = {
            "info": {
                "participants": [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
            }
        }
        for i in range(10):
            temp['info']["gameDuration"] = match['info']["gameDuration"]
            temp['info']["participants"][i]["champLevel"] = match['info']["participants"][i]["champLevel"]
            for j in range(6):
                temp['info']["participants"][i]["item" + str(j)] = match['info']["participants"][i]["item" + str(j)]
            temp['info']["participants"][i]["kills"] = match['info']["participants"][i]["kills"]
            temp['info']["participants"][i]["deaths"] = match['info']["participants"][i]["deaths"]
            temp['info']["participants"][i]["assists"] = match['info']["participants"][i]["assists"]
            temp['info']["participants"][i]["totalMinionsKilled"] = match['info']["participants"][i][
                "totalMinionsKilled"]
            temp['info']["participants"][i]["totalEnemyJungleMinionsKilled"] = match['info']["participants"][i][
                "totalEnemyJungleMinionsKilled"]
            temp['info']["participants"][i]["totalAllyJungleMinionsKilled"] = match['info']["participants"][i][
                "totalAllyJungleMinionsKilled"]
            temp['info']["participants"][i]["win"] = match['info']["participants"][i]["win"]

        with open(os.path.join('matches', "match{}.json".format(self.idx)), "w") as outfile:
            json.dump(temp, outfile, indent=2)
            self.idx += 1

    def get_player_id(self, name):
        name = urllib.parse.quote(name)
        API_URL = self.API_URL + name + '?api_key=' + self.API_KEY
        response = requests.get(API_URL)
        player_info = response.json()
        formatted_json = json.dumps(player_info, indent=4)
        self.puuid = player_info.get('puuid')

    def add_to_db(self):
        print(self.puuidset)
        with open("puuid.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            for puuid in self.puuidset:
                writer.writerow([puuid])
            file.close()

    def get_match_info(self, puuids):
        temp = []
        for puuid in puuids:
            print(len(self.puuidset))
            if len(self.puuidset) >= 1000:
                return
            idx = random.randint(1, 100)
            MATCHlist_URL = "{}{}/ids?start={}&count=1&api_key={}".format(self.MATCH_URL, puuid, idx, self.API_KEY)
            info = requests.get(MATCHlist_URL)
            MatchList = info.json()
            Matches = []
            for match in MatchList:
                Matches.append(match)

            for j in range(len(Matches)):
                time.sleep(1.21)
                MATCH_URL = self.MATCH_DETAIL_URL + Matches[j] + '?api_key=' + self.API_KEY
                info = requests.get(MATCH_URL)
                MatchDetail = info.json()

                if info.status_code != 200:
                    time.sleep(5)
                    continue
                if MatchDetail['info']['queueId'] == 420:
                    self.add_json(MatchDetail)
                    for i in range(10):
                        self.puuidset.add(MatchDetail['metadata']['participants'][i])
                        temp.append(MatchDetail['metadata']['participants'][i])

        self.Matches = []
        self.get_match_info(temp)
        return


puuid = ['eOS1WY-duN9a8AjoHte44f3cJ5oytHv3LDl4NGgiJwyswR2HOed5PFN_tzt5o69ClMZ32GJcKb7-UQ']
data = Data()
data.get_match_info(puuid)
