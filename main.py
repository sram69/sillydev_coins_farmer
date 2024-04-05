#import os
#os.system("pip install -r requirements.txt")

from colorama import init,Fore, Back, Style
from threading import Thread
from time import sleep
import datetime
import requests
import json
init()

class User:
    def __init__(self, apikey, color):
        self.apikey = apikey
        self.color = f'\033[{color}'
        self._running = False

        self._headers = {
            "Authorization": "Bearer "+apikey,
            "Content-Type": "application/json",
            "Accept": "Application/vnd.pterodactyl.v1+json"
        }

        self._baseURL = "https://panel.sillydev.co.uk/api/"

        r = requests.get(self._baseURL+"client/account", headers=self._headers)
        if r.status_code != 200: exit("Error: Invalid token")
        self.userdata = r.json()["attributes"]

    def _log(self, text):
        color_reset = f"{Fore.RESET}{Back.RESET}{Style.RESET_ALL}"
        
        time = datetime.datetime.now().strftime("%H:%M:%S %d/%m")
        print(f"{self.color}{self.userdata['username']}{color_reset} [{time}] {text}")

    def getBalance(self):
        r = requests.get("https://panel.sillydev.co.uk/api/client/store", headers=self._headers)
        if r.status_code != 200: exit("Error: Invalid token")
        return r.json()["attributes"]["balance"]
    
    def mainloop(self):
        while self._running:
            try:
                for i in range(0, 60):
                    sleep(1)
                    if not self._running: break

                r = requests.post(self._baseURL+"client/store/earn", headers=self._headers)
                if r.status_code == 204:
                    self._log(f"{self.getBalance()}$ | Coins redeemed")
                elif r.status_code == 429:
                    self._log(f"Error 429 | Waiting 60s")
                    for i in range(0, 60):
                        sleep(1)
                        if not self._running: break
            except Exception as err:
                self._log(f"Error while running: {err}")

    def start(self):
        self._running = True
        self._thread = Thread(target=self.mainloop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        self._running = False

users = json.load(open('users.json', 'r'))

accs = []
for name, key in users.items():
    TEMP = User(key[0], key[1])
    TEMP.start()
    accs.append(TEMP)

input()

for user in accs:
    user.stop()
