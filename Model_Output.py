from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask import Response, jsonify
import json
import pandas as pd
import xgboost as xgb
import numpy as np
import yfinance as yf

filename = 'SPY_Model.pkl'
loaded_model = xgb.Booster({'nthread': 4})  # init model
loaded_model.load_model(filename)

ticker_JSON = {}
ticker = ''

class retrieveTickerInfo(Resource): # Retrieve name of Ticker -> Go to Yahoo Finance and scrape, Day Open / Low / High, Volume
    def get(self):
        global ticker_JSON
        global ticker
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('ticker', required=True)  # add arguments
        args = parser.parse_args()  # parse arguments to dictionary
        ticker = args['ticker']

        string=['Previous Close', 'Open', 'Bid', 'Ask', 'Day Range', '52 Week Range', 'Volume', 'Avg. Volume']
        value = [] # Value

        profile = pd.read_html('https://finance.yahoo.com/quote/' + ticker)
        profile_df = pd.DataFrame(profile[0])

        for i in profile_df[1]:
            value.append(i)

        final_df = pd.DataFrame(data=[value], columns=string)
        print(final_df)
        final_df = final_df.to_dict() # Convert to "JSON". to_json() simply return escaped string
        ticker_JSON = jsonify(final_df)
        # ticker_JSON.status_code = 200 # or 400 or whatever
        return ticker_JSON

class predictPrice(Resource):
    def get(self):
        ticker_YF = yf.Ticker(ticker)
        print(ticker_YF)
        # return ticker_JSON


app = Flask(__name__)
api = Api(app)

api.add_resource(retrieveTickerInfo, '/retrieveTickerInfo')
api.add_resource(predictPrice, '/predictPrice')

if __name__ == '__main__':
    app.run(debug=False)