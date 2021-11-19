import requests
from bs4 import BeautifulSoup
import urllib.parse

"""
Write links of accounts with active comments in last week to "newUserLinks.txt"
"""

headers = {
    "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "referer" : "https://fark.com"
};

count = 0
hrefIdentifier = "href="
endArticleIdentifier = "target="
endUserIdentifier = "id="

articleLinks = []


r = requests.get("https://www.fark.com", headers=headers)
page = BeautifulSoup(r.content, 'html.parser')

# creative lambda function to parse all class tags which start with a certain attribute
# credit @ https://stackoverflow.com/a/35465898
articles = page.find_all("a", {"class" : lambda L: L and L.startswith('icon_comment')})

# get article links
with open("newLinks.txt", "w") as f:
    for article in articles:
        article = str(article)

        endLink = article.find(endArticleIdentifier) - 2

        link = article[article.find(hrefIdentifier) + len(hrefIdentifier) + 1: endLink]
        articleLinks.append(link)
        f.write(link + "\n")

# get comment profile links
with open("newUserLinks.txt", "r+") as g:
    for i, link in enumerate(articleLinks):
        r = requests.get(link, headers=headers)
        articleSoup = BeautifulSoup(r.content, 'html.parser')

        commentRef = articleSoup.find('div', id='commentsArea')

        userDetails = commentRef.find_all('a', {"id" : lambda L: L and L.startswith('cu')})

        for userComment in userDetails:
            rawName = userComment.contents[0]

            encodedName = urllib.parse.quote(rawName)

            g.write("https://fark.com/users/" + encodedName + '\n')
