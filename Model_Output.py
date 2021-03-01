from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask import Response, jsonify
import json
import pandas as pd
import xgboost as xgb
import numpy as np
import yfinance as yf
import requests

filename = 'SPY_Model.pkl'
loaded_model = xgb.Booster({'nthread': 4})  # init model
loaded_model.load_model(filename)

class predictPrice(Resource):
    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('ticker', required=True)  # add arguments
        args = parser.parse_args()  # parse arguments to dictionary
        ticker = args['ticker']

        ticker_YF = yf.Ticker(ticker)
        ticker_YF = ticker_YF.get_info() # Retrieves information on the said Ticker

        price_open = ticker_YF['open']
        high = ticker_YF['dayHigh']
        low = ticker_YF['dayLow']
        volume = ticker_YF['volume']

        # Convert to dataframe to prepare for JSON conversion
        prediction_pd = pd.DataFrame(data=[[price_open, high, low, volume]], columns=['Open', 'High', 'Low', 'Volume'])
        prediction_pd_JSON = prediction_pd.to_dict() # Converting to dictionary before converting it to JSON

        prediction = xgb.DMatrix(prediction_pd) # Creating the DMatrix with the Dataframe
        prediction = loaded_model.predict(prediction) # Predicting the price using the DMatrix

        # Convert to dataframe to prepare for JSON conversion
        prediction_JSON = pd.DataFrame(data=[prediction], columns=['Predicted Value'])
        prediction_JSON = prediction_JSON.to_dict() # Converting to dictionary before converting it to JSON
        
        return jsonify(prediction_pd_JSON, prediction_JSON)

app = Flask(__name__)
api = Api(app)

api.add_resource(predictPrice, '/predictPrice')

if __name__ == '__main__':
    app.run(debug=False)