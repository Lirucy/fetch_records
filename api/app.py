from flask import Flask, g 

from db import DATABASE, initialize
from transaction import Transaction
from resources.transactions import transaction

DEBUG = True
PORT = 8000

app = Flask(__name__)

app.secret_key = 'fetchrewardssuperdupersecretkey'

@app.before_request
def before_request():
    g.db = DATABASE
    g.db.connect()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/')
def index():
    return 'Welcome to the FetchRewards code challenge!'

app.register_blueprint(transaction)

if __name__ == '__main__':
    initialize([Transaction])
    app.run(debug=DEBUG, port=PORT)

