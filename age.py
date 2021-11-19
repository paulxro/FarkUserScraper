import requests
from bs4 import BeautifulSoup
import urllib.parse
import datetime
import json

"""
Populate "userInfo.json" with user profiles collected using "account.py"
"""

headers = {
    "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "referer" : "https://fark.com"
};

class UserObject:
    def __init__(self, encodedUsername, link, accountNumber, accountCreated, linksRef):
        self.encodedUsername = encodedUsername
        self.username = urllib.parse.unquote(self.encodedUsername)
        self.link = link
        self.accountNumber = accountNumber
        self.accountCreated = datetime.datetime.strptime(accountCreated.strip().split()[0], "%Y-%m-%d")
        self.accountAge = datetime.datetime.now().year - self.accountCreated.year
        self.linksRef = linksRef.strip()

userLinks = []
userObjects = []
rawLink = "https://fark.com/users/"
userJsons = []

# read links to user profiles into "userLinks"
with open("newUserLinks.txt", "r") as f:
    for line in f.read().splitlines():
        userLinks.append(line)

# clear json
with open("userInfo.json", "w") as f:
    f.write("{}")


with open("userInfo.csv", "w") as f:
    f.write("username,encodedUsername,link,accountNumber,accountCreated,accountAge,linksRef\n")
    for i, link in enumerate(userLinks):

        alreadyExists = False
        # Prevent bad requests from throwing exceptions
        try:
            r = requests.get(link, headers=headers)
        except:
            continue

        soup = BeautifulSoup(r.content, 'html.parser')

        username = link[len(rawLink):]

        # Move to next user if user is already known
        for user in userObjects:
            if user.encodedUsername == username:
                continue

        # print(f'Gathering information for: {urllib.parse.unquote(username)}', end = '')

        rawUserInfoArea = soup.find("table", class_ = "profileTable")

        # Important info lies in indices 1-3, inclusive, of the "profileTable" class tag
        userInfoList = []
        for i in range(1,4):
            userInfoList.append(rawUserInfoArea.find_all("td", class_ = "proftxt")[i].contents[0])

        try:
            newUser = UserObject(username, link, userInfoList[0], userInfoList[1], userInfoList[2])
        except:
            continue

        userObjects.append(newUser)

        # work-around due to datetime.datetime object (UGH)
        f.write(
            f'{newUser.username},{newUser.encodedUsername},{newUser.link},{newUser.accountNumber},' +
            f'{newUser.accountCreated.strftime("%Y-%m-%d")},{newUser.accountAge},{newUser.linksRef}\n'
        )

        # also save output as json for easy future parsing
        userJson = {
            "username" : newUser.username,
            "encodedUsername" : newUser.encodedUsername,
            "link" : newUser.link,
            "accountNumber" : newUser.accountNumber,
            "accountCreated" : newUser.accountCreated.strftime("%Y-%m-%d"),
            "accountAge" : newUser.accountAge,
            "linksRef" : newUser.linksRef
        }

        userJsons.append(userJson)

        # print(' Done...')

with open("userInfo.json", "r+") as f:
    json.dump(userJsons, f, indent=4)


# random info calculation (avg. account age)
total = 0.0
for user in userObjects:
    total += user.accountAge

print("Average account age:", total/len(userObjects))


