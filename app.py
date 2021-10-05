# Pure Python
import requests
# Framework
from flask import Flask, request, render_template, session
# Custom
from config import tink_config
app = Flask(__name__)
app.secret_key = "sldkjflkdsjflkasj6876876809324)*&*()R*#()$*"

# Global
# ACCESS_TOKEN = ''
# TEST = "Siwasdjlfks"


@app.route('/')
@app.route('/home')
@app.route('/index')
def index():  # put application's code here
    return render_template("index.html")


@app.route('/callback')
def callback():
    code = request.args.get('code')
    # tink_config.HOST+"/oauth/token"
    r = requests.post("https://api.tink.com/api/v1/oauth/token", data={"code": code, "client_id": tink_config.CLIENT_ID,
                                                   "client_secret": tink_config.SECRET_KEY,
                                                   "grant_type": "authorization_code"}
                      )
    if r.status_code == requests.codes.ok:
        # print("before " + r['access_token'])
        print(r)
        r = r.json()
        print(r)
        session["access_token"] = r['access_token']
        print("ACCESS TOKEN IS "+session["access_token"])
    else:
        print("error connecting")
    return render_template("transaction.html")

@app.route('/transactions')
def transaction():
    print("here access token is "+session["access_token"])
    headers = {'Authorization': 'Bearer ' + session["access_token"]}
    payload = {'pageSize': 10}
    r = requests.get("https://api.tink.com/data/v2/transactions", headers=headers, params=payload)
    transactions = []
    if r.status_code == requests.codes.ok:
        print(r.json())
        r = r.json()
        transactions = r["transactions"]
    else:
        print(r)
        print("Error getting transactions")
    return render_template("transaction.html", transactions=transactions)



if __name__ == '__main__':
    app.run()
