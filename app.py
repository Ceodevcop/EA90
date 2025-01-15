import hashlib
import hmac
import time
import json
import requests
from flask import Flask, render_template, request, jsonify

# Bitget API credentials
API_KEY = 'bg_ffcbb26a743c6f3617a03e4edb87aa3f'  # Replace with your actual API key
API_SECRET = 'e397e3420dbb6a1b48dfef734e6ef8d6aaf29ee44a044d51dd1742a8143c0693'  # Replace with your actual API secret
API_PASSPHRASE = '02703242'  # Replace with your passphrase if applicable

# API base URL
BASE_URL = "https://api.bitget.com"

# Parameters for grid trading
GRID_SIZE = 5
GRID_DISTANCE = 50
LOT_SIZE = 0.001
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']

# Initialize Flask app
app = Flask(__name__)

# Function to generate the signature for the request
def generate_signature(timestamp, method, request_path, query_string='', body=''):
    body = json.dumps(body) if isinstance(body, dict) else body
    if method == "POST":
        body = body if body else ""
    else:
        body = ""

    # Concatenate all the elements that need to be signed
    message = timestamp + method + request_path + query_string + body
    signature = hmac.new(API_SECRET.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
    
    return signature

# Function to make a request to Bitget API
def api_request(endpoint, method='GET', params=None, body=None):
    url = BASE_URL + endpoint

    # Get timestamp for signing
    timestamp = str(int(time.time() * 1000))  # Millisecond timestamp

    # Build the query string (if any)
    query_string = ''
    if params:
        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])

    # Generate the signature
    signature = generate_signature(timestamp, method, endpoint, query_string, body)

    # Set the request headers
    headers = {
        'Content-Type': 'application/json',
        'Bitget-APIKey': API_KEY,
        'Bitget-Signature': signature,
        'Bitget-Timestamp': timestamp,
        'Bitget-Passphrase': API_PASSPHRASE,
    }

    # Perform the request based on the method
    if method == 'GET':
        response = requests.get(url, headers=headers, params=params)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=body)

    # Check if the response is successful
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Request failed", "status_code": response.status_code, "message": response.text}

# Function to get market price for a symbol
def get_market_price(symbol):
    endpoint = f"/api/spot/v1/market/ticker?symbol={symbol}"
    response = api_request(endpoint)
    if 'data' in response:
        return response['data'][0]['last']
    else:
        return "Error fetching price"

# Function to place orders for grid trading
def place_order(symbol, side, price, quantity):
    endpoint = '/api/spot/v1/orders'
    order_data = {
        'symbol': symbol,
        'side': side,
        'price': str(price),
        'size': str(quantity),
        'type': 'limit',
        'timeInForce': 'GTC'
    }
    response = api_request(endpoint, method='POST', body=order_data)
    return response

# Function to perform grid trading logic
def grid_trading():
    for symbol in SYMBOLS:
        current_price = float(get_market_price(symbol))
        print(f"Current Market Price for {symbol}: {current_price}")

        for i in range(GRID_SIZE):
            buy_price = current_price - (GRID_DISTANCE * (i + 1))
            sell_price = current_price + (GRID_DISTANCE * (i + 1))

            place_order(symbol, 'buy', buy_price, LOT_SIZE)
            print(f"Placed Buy Order for {symbol} at {buy_price}")

            place_order(symbol, 'sell', sell_price, LOT_SIZE)
            print(f"Placed Sell Order for {symbol} at {sell_price}")

# Flask Routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_trading', methods=['POST'])
def start_trading():
    grid_trading()
    return jsonify({"status": "success", "message": "Grid trading started."})

@app.route('/stop_trading', methods=['POST'])
def stop_trading():
    # Logic to stop trading (optional based on your use case)
    return jsonify({"status": "success", "message": "Grid trading stopped."})

@app.route('/get_price/<symbol>', methods=['GET'])
def get_price(symbol):
    price = get_market_price(symbol)
    return jsonify({"symbol": symbol, "price": price})

if __name__ == '__main__':
    app.run(debug=True)
