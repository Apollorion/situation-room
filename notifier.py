import requests
import os
import helpers

groups = helpers.get_groups()
posts = helpers.get_posts()
last_update = helpers.get_last_update()

def update_message(post, key, title, _message):
    if post[key] is not None:
        _message += f"<b>{title}</b>: {post[key]}\n"
    return _message

for post in posts:
    if post["url"] == last_update:
        break

    print()
    print()
    print()
    home = post["home"]
    away = post["away"]

    print("Teams: ", home, away)

    notification_groups = [groups[helpers.group_to_team[home]], groups[helpers.group_to_team[away]]]

    print(f"notification groups: {notification_groups}")

    title = f"{home} vs {away}: {post['type']}"

    message = update_message(post, "short_description", "Desc", "")
    message = update_message(post, "challenge_initiator", "Initiated By", message)
    message = update_message(post, "type_of_challenge", "Challenge Type", message)
    message = update_message(post, "result", "Result", message)
    message = update_message(post, "explanation", "Explanation", message)
    message = update_message(post, "penalty", "Penalty", message)

    for group in notification_groups:
        print(f"Sending notification to {group}")
        r = requests.post("https://api.pushover.net/1/messages.json", data={
            "token": os.environ["PUSHOVER_APPLICATION_TOKEN"],
            "user": group,
            "title": title,
            "message": message,
            "ttl": 3600,
            "html": 1
        })
        print("Begin Response")
        print(r.json())
        print("End Response")

helpers.write_last_update(posts[0]["url"])
print()
print()
print()
print("Complete!")