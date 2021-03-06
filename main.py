import json
import os
import re
from collections import defaultdict
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from piazza_api import Piazza
from piazza_api.exceptions import AuthenticationError, RequestError

load_dotenv()

urls = re.compile(
    r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")
gist_splitter = re.compile(r'\/gist\/(\w+)\/(\w+)')

credentials = (os.environ['GITHUB_USER'], os.environ['GITHUB_PASSWORD'])
homework_posts_url = f"https://github.gatech.edu/raw/gist/{os.environ['GITHUB_USER']}/" + \
                     f"{os.environ['GITHUB_GIST']}/raw/homework_posts.json"

update_url = f"https://github.gatech.edu/api/v3/gists/{os.environ['GITHUB_GIST']}"


def extract_gists(post_id, network):
    """
    Retrieve the gist ids and authors from a specific post.
    :param post_id: the post to scrape
    :param network: the network
    :return: a dictionary of all gists by user
    """
    try:
        post = network.get_post(post_id)
    except RequestError:
        print(f"Error in retrieving post {post_id}. Check the class ID and post ID.")
        raise

    links = set(urlparse(x[0]) for response in post['children'] if 'subject' in response
                for x in urls.findall(response['subject']))
    links = [gist_splitter.match(link.path) for link in links if link.netloc == 'github.gatech.edu']
    links = [x.groups() for x in links if x]
    gists = defaultdict(list)
    for user, gist in links:
        gists[user].append(gist)
    return gists


def get_post_ids():
    """
    Fetch the desired post ids from the GitHub gist.
    :return: target homework posts ids
    """
    res = requests.get(homework_posts_url, auth=credentials)
    if res.status_code != 200:
        print('Error in reading the homework_posts.json file.')
        print(res.text)
        exit(1)
    return res.json()


def main():
    """
    Do da tings
    """
    p = Piazza()
    try:
        print('Authenticating into Piazza...')
        p.user_login(os.environ['PIAZZA_EMAIL'], os.environ['PIAZZA_PASSWORD'])
    except AuthenticationError:
        print('Piazza username or password incorrect.')
        exit(1)

    network = p.network(os.environ['PIAZZA_CLASS_ID'])

    print('Fetching target posts...')
    posts = get_post_ids()

    print('Extracting Gist URLs from posts...')
    gists = dict((homework, extract_gists(post_id, network)) for homework, post_id in posts.items())

    print('Uploading consolidated Gists to GitHub...')
    encoded = json.dumps(gists)
    res = requests.patch(update_url, data=json.dumps({'files': {'homework_meta.json': {'content': encoded}}}),
                         auth=credentials)
    if res.status_code != 200:
        print('Error in updating the homework_meta.json file.')
        print(res.text)
        exit(1)

    print('Done!')


if __name__ == "__main__":
    main()
