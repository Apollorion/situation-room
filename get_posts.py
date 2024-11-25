import bs4
import requests
import json
from datetime import datetime

base_url = "https://www.nhl.com"

class Post:
    def __init__(self, text, url):
        self.text = transfigure(text)
        self.url = transfigure(url)

        self.post_text = None

    def get_text(self):
        return transfigure(self.text)

    def get_type(self):
        return transfigure(self.text.split(": ")[0])

    def get_home(self):
        return transfigure(self.text.split(": ")[1].split(" @ ")[0])

    def get_away(self):

        self.text.split(": ")[1].split(" @ ")[1].split("-")[0]

        return transfigure(self.text.split(": ")[1].split(" @ ")[1].split("-")[0])

    def get_short_description(self):
        if self.get_type() == "Officials Update":
            return None

        return transfigure(self.text.split("-")[1])

    def get_url(self):
        return transfigure(self.url)

    def _fill(self):
        soup = soupify(f"{base_url}{self.url}")
        article = soup.find('article')

        article_body = article.find('div', {'class': 'oc-c-body-part oc-c-markdown-stories'})

        self.post_text = transfigure(article_body.text)

    def get_challenge_initiator(self):
        if self.post_text is None:
            self._fill()

        if "Challenge Initiated By: " not in self.post_text:
            return None

        return transfigure(self.post_text.split("Challenge Initiated By: ")[1].split("\n")[0])

    def get_type_of_challenge(self):
        if self.post_text is None:
            self._fill()

        if "Type of Challenge: " not in self.post_text:
            return None

        return transfigure(self.post_text.split("Type of Challenge: ")[1].split("\n")[0])

    def get_result(self):
        if self.post_text is None:
            self._fill()

        if self.get_type() == "Officials Update":
            return transfigure(self.post_text)

        if "Result: " not in self.post_text:
            return None

        return transfigure(self.post_text.split("Result: ")[1].split("\n")[0])

    def get_explination(self):
        if self.post_text is None:
            self._fill()

        if "Explanation: " not in self.post_text:
            return None

        return transfigure(self.post_text.split("Explanation: ")[1].split("\n")[0])

    def get_penalty(self):
        if self.post_text is None:
            self._fill()

        if "Penalty: " not in self.post_text:
            return None

        return transfigure(self.post_text.split("Penalty: ")[1].split("\n")[0])

    def dumps(self):
        print(f"Dumping {self.url}")
        return {
            "type": self.get_type(),
            "home": self.get_home(),
            "away": self.get_away(),
            "short_description": self.get_short_description(),
            "url": self.url,
            "challenge_initiator": self.get_challenge_initiator(),
            "type_of_challenge": self.get_type_of_challenge(),
            "result": self.get_result(),
            "explanation": self.get_explination(),
            "penalty": self.get_penalty()
        }

def transfigure(text):
    return (text
            .replace("\u2013", "-")
            .replace("\u2019", "'")
            .replace("\u00a0", " ")
            .replace("\u201c", '"')
            .replace("\u201c", '"')
            .replace("\u201d", '"')
            .strip())

def soupify(url):
    r = requests.get(url)
    return bs4.BeautifulSoup(r.content, 'html.parser', from_encoding="utf-8")

# Get the posts from https://www.nhl.com/news/topic/situation-room/
def get_posts():
    date_time_string = datetime.now().strftime("%d-%m-%YT%H-%M-%S")
    url = f"{base_url}/news/topic/situation-room/?date_cache_busting={date_time_string}"
    print(f"Getting all posts from: {url}")
    soup = soupify(url)
    posts = soup.find_all('div', {'class': 'd3-l-col__col-3'})

    classed_posts = []
    for post in posts:
        title = post.find('h3').text
        url = post.find('a')['href']

        try:
            p = Post(title, url)
            classed_posts.append(p.dumps())
        except Exception as e:
            print(f"Error safely continuing: {e}")

    return classed_posts

posts = get_posts()
# Write the posts to a file
print("Writing posts to file...")
with open("storage/posts.json", "w") as f:
    f.write(json.dumps(posts, indent=4))
print("Complete!")