from flask import Flask, redirect
from flask import request
import requests
import helpers
import os

app = Flask(__name__)

def generate_page(title, content, margin="10%"):
    return f"""
    <head>
        <title>{title}</title>
    </head>
    <body style="background-color: grey; color: white; text-align: center; margin: {margin};>
        <div style="text-align: center;">
            {content}
        </div>
    </body>
    """

@app.route("/")
def subscribe():
    success = request.args.get("success")
    if success is not None:
        return generate_page("SUCCESS", "<h1>You have successfully subscribed to The Situation Room!</h1><div>Manage your subscriptions in the Pushover app.</div>")

    content = """
    <h1>Welcome to The Situation Room</h1>
    <div>Have you ever wondered "why in the hell did they make that call!?" during an NHL game?</div>
    <div>We sync live data, from the NHL situation room straight to your devices using Pushover to let you know their reasoning (not that we'll agree with it).</div>
    <br/>
    <div>
        <div>Its as simple as:</div>
        <div style="display: inline-block; text-align: left;">
        <ol>
            <li>Download the pushover app from the google play or apple app store.</li>
            <li>Click the "Subscribe with pushover" button below.</li>
            <li>Login to your pushover account.</li>
            <li>Choose the teams you want to subscribe to.</li>
        </ol>
        </div>
        <div>Once this is done, whenever the NHL Situation Room makes a call involving your team, you'll get a notification with their reasoning.</div>
    </div>
    <br/>
    <div>
        <style type="text/css">
            .pushover_button {
                box-sizing:border-box !important;display:inline-block;background-color:#eee !important;background: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAycHgiIGhlaWdodD0iNjAycHgiIHZlcnNpb249IjEuMSIgdmlld0JveD0iNTcgNTcgNjAyIDYwMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSg1OC45NjQgNTguODg4KSIgb3BhY2l0eT0iLjkxIj48ZWxsaXBzZSB0cmFuc2Zvcm09Im1hdHJpeCgtLjY3NDU3IC43MzgyMSAtLjczODIxIC0uNjc0NTcgNTU2LjgzIDI0MS42MSkiIGN4PSIyMTYuMzEiIGN5PSIxNTIuMDgiIHJ4PSIyOTYuODYiIHJ5PSIyOTYuODYiIGZpbGw9IiMyNDlkZjEiIGZpbGwtcnVsZT0iZXZlbm9kZCIgc3Ryb2tlLXdpZHRoPSIwIi8+PHBhdGggZD0ibTI4MC45NSAxNzIuNTFsNzQuNDgtOS44LTcyLjUyIDE2My42NmMxMi43NC0wLjk4IDI1LjIzMy01LjMwNyAzNy40OC0xMi45OCAxMi4yNTMtNy42OCAyMy41MjctMTcuMzE3IDMzLjgyLTI4LjkxIDEwLjI4Ny0xMS42IDE5LjE4Ny0yNC41MDMgMjYuNy0zOC43MSA3LjUxMy0xNC4yMTMgMTIuOTAzLTI4LjE4IDE2LjE3LTQxLjkgMS45Ni04LjQ5MyAyLjg2LTE2LjY2IDIuNy0yNC41LTAuMTY3LTcuODQtMi4yMS0xNC43LTYuMTMtMjAuNThzLTkuODgzLTEwLjYxNy0xNy44OS0xNC4yMWMtOC0zLjU5My0xOC44Ni01LjM5LTMyLjU4LTUuMzktMTYuMDA3IDAtMzEuNzcgMi42MTMtNDcuMjkgNy44NC0xNS41MTMgNS4yMjctMjkuODg3IDEyLjgyMy00My4xMiAyMi43OS0xMy4yMjcgOS45Ni0yNC43NCAyMi4zNzMtMzQuNTQgMzcuMjQtOS44IDE0Ljg2LTE2LjgyMyAzMS43NjMtMjEuMDcgNTAuNzEtMS42MzMgNi4yMDctMi42MTMgMTEuMTg3LTIuOTQgMTQuOTQtMC4zMjcgMy43Ni0wLjQwNyA2Ljg2My0wLjI0IDkuMzEgMC4xNiAyLjQ1MyAwLjQ4MyA0LjMzMyAwLjk3IDUuNjQgMC40OTMgMS4zMDcgMC45MDMgMi42MTMgMS4yMyAzLjkyLTE2LjY2IDAtMjguODMtMy4zNS0zNi41MS0xMC4wNS03LjY3My02LjY5My05LjU1LTE4LjM3LTUuNjMtMzUuMDMgMy45Mi0xNy4zMTMgMTIuODIzLTMzLjgxIDI2LjcxLTQ5LjQ5IDEzLjg4LTE1LjY4IDMwLjM3My0yOS40ODMgNDkuNDgtNDEuNDEgMTkuMTEzLTExLjkyIDQwLjAyLTIxLjM5IDYyLjcyLTI4LjQxIDIyLjcwNy03LjAyNyA0NC44NC0xMC41NCA2Ni40LTEwLjU0IDE4Ljk0NyAwIDM0Ljg3IDIuNjkzIDQ3Ljc3IDguMDggMTIuOTA3IDUuMzkzIDIyLjk1MyAxMi41IDMwLjE0IDIxLjMyczExLjY3NyAxOS4xMSAxMy40NyAzMC44N2MxLjggMTEuNzYgMS4yMyAyNC4wMS0xLjcxIDM2Ljc1LTMuNTkzIDE1LjM1My0xMC4zNzMgMzAuNzktMjAuMzQgNDYuMzEtOS45NiAxNS41MTMtMjIuNDUzIDI5LjU2LTM3LjQ4IDQyLjE0LTE1LjAyNyAxMi41NzMtMzIuMjYgMjIuNzgtNTEuNyAzMC42Mi0xOS40MzMgNy44NC00MC4wOTMgMTEuNzYtNjEuOTggMTEuNzZoLTIuNDVsLTYyLjIzIDEzOS42NWgtNzAuNTZsMTM4LjY3LTMxMS42NHoiIGZpbGw9IiNmZmYiIHN0eWxlPSJ3aGl0ZS1zcGFjZTpwcmUiLz48L2c+PC9zdmc+) 3px 3px no-repeat;background-size:15px 15px;border-bottom:2px solid rgba(22,22,22,0.25) !important;border-right:2px solid rgba(22,22,22,0.25) !important;box-shadow: 0pt 2px 0pt rgba(255, 255, 255, 0.2) inset, 0pt 2px 0px rgba(0, 0, 0, 0.05) !important;border-radius:3px !important;color:#333 !important;display:inline-block !important;font:11px/18px "Helvetica Neue",Arial,sans-serif !important;font-weight:bold !important;cursor:pointer !important;height:22px !important;padding:1px 6px 20px 22px!important;overflow:hidden !important;text-decoration:none !important;vertical-align:middle !important;height:22px !important;
            }
        </style>
        
        <a class="pushover_button" href="https://pushover.net/subscribe/TheSituationRoom-tkoyepmdc33ncz3?success=https%3A%2F%2Fsituationroom.apollorion.com%2Fsubscribe-choose-team&failure=https%3A%2F%2Fsituationroom.apollorion.com%2Fsubscribe-fail">
            Subscribe With Pushover
        </a>
    </div>
    """

    return generate_page("The Situation Room", content)

@app.route("/subscribe-choose-team")
def subscribe_choose_team():
    user_id = request.args.get("pushover_user_key")

    # create a selection of teams to subscribe to
    team_selection = []
    for group in helpers.group_to_team:
        team_selection.append({
            "label": helpers.group_to_team[group],
            "value": group
        })

    # Generate input box in html
    team_selection_html = ""
    for team in team_selection:
        team_selection_html += f"""
        <input type="checkbox" name="team[]" value="{team['value']}">
        <label for="{team['value']}">{team['label']}</label><br>
        """

    form = f"""
    <form action="/subscribe-final?pushover_user_key={user_id}" method="post">
    {team_selection_html}
    <br/>
    <input type="email" name="email" maxlength="100" placeholder="Your email address" required>
    <br/><br/>
    <input type="submit" value="Finalize Subscription">
    </form>
    """

    html = f"""
    <div>
    <h1>Choose Teams</h1>
    <div>Choose the teams you would like to subscribe to:</div>
    <br/>
    <div style="display: inline-block; text-align: left;">
    {form}
    </div>
    </div>
    """

    return generate_page("Choose Teams", html, margin="1%")

@app.route("/subscribe-final", methods=["POST"])
def subscribe_final():
    user_id = request.args.get("pushover_user_key")

    teams = request.form.getlist("team[]")
    email = request.form.get("email")
    groups = helpers.get_groups()

    for team in teams:
        team_group_key = helpers.group_to_team[team]
        r = requests.post(f"https://api.pushover.net/1/groups/{groups[team_group_key]}/add_user.json", data={
            "token": os.environ["PUSHOVER_APPLICATION_TOKEN"],
            "user": user_id,
            "memo": email
        })
        print(r.json())

    return redirect('/?success=true')

@app.route("/subscribe-fail")
def subscribe_fail():
    return "There was an error subscribing to The Situation Room. You can email me if this was a mistake: joey@apollorion.com"