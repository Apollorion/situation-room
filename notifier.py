import requests
import os
import helpers

groups = helpers.get_groups()
posts = helpers.get_posts()
last_update = helpers.get_last_update()

for post in posts:
    if post["url"] == last_update:
        break

    home = post["home"]
    away = post["away"]

    notification_groups = [groups[helpers.group_to_team[home]], groups[helpers.group_to_team[away]]]

    print(f"Post Processing For Teams: {home} {away}, notification groups: {notification_groups}")

    for group in notification_groups:
        print(f"Sending notification to {group}")
        r = requests.post("https://api.pushover.net/1/messages.json", data={
            "token": os.environ["PUSHOVER_APPLICATION_TOKEN"],
            "user": group,
            "title": post["type"],
            "message": f"{post['short_description']} - {post['explanation']}",
        })
        print("Begin Response")
        print(r.json())
        print("End Response")

helpers.write_last_update(posts[0]["url"])
print("Complete!")