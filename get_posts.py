import json
from datetime import UTC, datetime

import bs4
import requests
from opentelemetry.instrumentation.requests import RequestsInstrumentor

import helpers
import otel_config

# Initialize OpenTelemetry
tracer = otel_config.init_telemetry("situation-room-scraper", "1.0.0")

# Instrument requests library for automatic HTTP tracing
# Exclude OTEL collector endpoints to prevent instrumentation loops
RequestsInstrumentor().instrument(
    excluded_urls=".*v1/traces.*,.*opentelemetry-collector.*"
)

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
        with tracer.start_as_current_span("post.fill_details") as span:
            span.set_attribute("post.url", self.url)
            soup = soupify(f"{base_url}{self.url}")
            article = soup.find('article')

            article_body = article.find('div', {'class': 'oc-c-body-part oc-c-markdown-stories'})

            self.post_text = transfigure(article_body.text)
            span.set_attribute("post.text_length", len(self.post_text))

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
        otel_config.logger.info("parsing post")
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
    with tracer.start_as_current_span("html.parse") as span:
        span.set_attribute("http.url", url)
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        span.set_attribute("http.status_code", r.status_code)
        span.set_attribute("http.response_size", len(r.content))
        return bs4.BeautifulSoup(r.content, 'html.parser', from_encoding="utf-8")

# Get the posts from https://www.nhl.com/news/topic/situation-room/
def get_posts():
    with tracer.start_as_current_span("scraper.get_posts") as span:
        date_time_string = datetime.now(UTC).strftime("%d-%m-%YT%H-%M-%S")
        url = f"{base_url}/news/topic/situation-room/?date_cache_busting={date_time_string}"
        otel_config.logger.info("fetching posts")
        span.set_attribute("scraper.url", url)

        soup = soupify(url)
        posts = soup.find_all('div', {'class': 'd3-l-col__col-3'})
        span.set_attribute("scraper.posts_found", len(posts))

        classed_posts = []
        for post in posts:
            title = post.find('h3').text
            url = post.find('a')['href']

            last_update = helpers.get_last_update()
            if url == last_update:
                otel_config.logger.info("scraper cursor reached")
                break

            try:
                p = Post(title, url)
                classed_posts.append(p.dumps())
            except Exception as e:
                otel_config.record_failure(span, e)

        span.set_attribute("scraper.new_posts", len(classed_posts))
        return classed_posts

posts = get_posts()

if len(posts) > 0:
    # Write the posts to a file
    otel_config.logger.info("writing posts")
    with tracer.start_as_current_span("scraper.write_posts"), open("storage/posts.json", "w") as f:
        f.write(json.dumps(posts, indent=4))
else:
    otel_config.logger.info("no new posts")
otel_config.logger.info("scraper completed")
