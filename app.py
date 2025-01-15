from flask import Flask, render_template, request, jsonify
import time
from bitget_api_utils import api_request, get_market_price

app = Flask(__name__)

# Parameters for grid trading
GRID_SIZE = 5
GRID_DISTANCE = 50
LOT_SIZE = 0.001
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']

# Example function to start grid trading for a symbol
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

@app.route('/')
def index():
    # Render the frontend UI
    return render_template('index.html')

@app.route('/start_trading', methods=['POST'])
def start_trading():
    grid_trading()
    return jsonify({"status": "success", "message": "Grid trading started."})

@app.route('/get_price/<symbol>', methods=['GET'])
def get_price(symbol):
    price = get_market_price(symbol)
    return jsonify({"symbol": symbol, "price": price})

if __name__ == '__main__':
    app.run(debug=True)
