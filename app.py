# Pure Python
from datetime import date
import requests
# Framework
from flask import Blueprint, Flask, request, render_template, session, redirect, url_for
# Custom
from config import tink_config
app = Flask(__name__)
app.secret_key = "sldkjflkdsjflkasj6876876809324)*&*()R*#()$*"

views = Blueprint("views", __name__)


@app.route('/')
@app.route('/home')
@app.route('/index')
def index():  # put application's code here
    return render_template("index.html")


@app.route('/callback')
def callback():
    code = request.args.get('code')
    r = requests.post(tink_config.HOST + "api/v1/oauth/token", data={"code": code, "client_id": tink_config.CLIENT_ID,
                                                   "client_secret": tink_config.SECRET_KEY,
                                                   "grant_type": "authorization_code"}
                      )
    if r.status_code == requests.codes.ok:
        r = r.json()
        session["access_token"] = r['access_token']
    else:
        print("error connecting")
        return render_template("index.html")
    return redirect(url_for('task1'))


@app.route('/task1')
def task1():
    headers = {'Authorization': 'Bearer ' + session["access_token"]}
    payload = {'pageSize': 10}
    r = requests.get(tink_config.HOST + "data/v2/transactions", headers=headers, params=payload)
    transactions = []
    if r.status_code == requests.codes.ok:
        r = r.json()
        transactions = r["transactions"]
    else:
        print("Error getting transactions")
        return render_template("index.html")
    return render_template("transaction.html", transactions=transactions)

@app.route('/task2')
def task2():
    headers = {'Authorization': 'Bearer ' + session["access_token"]}
    payload = {'pageSize': 500} # max 100 are allowed even if you give pageSize greater than 500
    r = requests.get(tink_config.HOST + "data/v2/transactions", headers=headers, params=payload)
    if r.status_code == requests.codes.ok:
        r = r.json()
        transactions = r["transactions"]
        transactions = filter(datefilter, transactions)
        final_transactions = []
        for transaction in transactions:
            found = False
            for i, each in enumerate(final_transactions):
                if transaction["descriptions"]["display"] == each["description"]:
                    each["count"] += 1
                    found = True
            if found == False:
                final_transactions.append({"count": 1, "description": transaction["descriptions"]["display"]})

        final_transactions = sort(final_transactions)

    else:
        print("Error getting transactions")
        return render_template("index.html")

    return render_template("task2.html", transactions=final_transactions)


def datefilter(transaction):
    last_months_allow = 3

    year = int(transaction['dates']['booked'][0:4])
    month = int(transaction['dates']['booked'][5:7])
    day = int(transaction['dates']['booked'][8:10])
    todays_date = date.today()

    if year != todays_date.year:
        return False

    # 10 >= 10 and 10 >= 7 => True
    # 10 >=11 and => False
    # 10 >= 9 and 9 >= 7 => True
    # 10 >= 7 and 7 >= 7 => True
    # 10 >= 6 and 6 >= 7 => False
    # 1 >= 12 and 12 >= -2

    if todays_date.month - last_months_allow <= 0:
        if (month != todays_date.month and month not in range(12,12-last_months_allow+todays_date.month-1,-1) and month not in range(1,todays_date.month)):
            return False
    elif not (todays_date.month >= month and month >= todays_date.month - last_months_allow):
        return False

    if month == todays_date.month - last_months_allow:
        if day < todays_date.day:
            return False
    return True

def sort(transactions):
    return sorted(transactions, key=lambda x: x['count'], reverse=True)

if __name__ == '__main__':
    app.run()
