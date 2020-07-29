import time
from pydelicious import get_popular, get_userposts, get_urlposts


def initialize_user_dict(tag, count =5):
    users = {}

    # get top $count posts
    posts = get_popular(tag=tag)[:count]
    #get users shares this tag post
    for p1 in posts:
        for p2 in get_userposts(p1["href"]):
            user = p2["user"]
            users[user] = {}

    return users

def fill_items(users):
    all_items = {}
    # get all links posted
    for user in users:
        for i in range(3):
            try:
                posts = get_userposts(user)
                break
            except Exception:
                print("Failed user '+user+', retrying ")
                time.sleep(4)
        for post in posts:
            url = post["href"]
            users[user][url] = 1.0
            all_items[url] = 1

        # assign 0 to not rated items
        for ratings in users.values():
            for item in all_items:
                if item not in ratings:
                    ratings[item] = 0.0


