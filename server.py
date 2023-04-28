import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/process-json', methods=['POST'])
def process_json():
    # Get the JSON data from the request
    data = request.get_json()

    # Extract the relevant information from the JSON data
    order_number = data['Order Number']
    time = data['Time']
    items = data['items']

    # Generate the markup based on the extracted information
    markup = f"[magnify: width 2; height 2]\n[column: left ORDER {order_number}; right Time {time}]\n"

    for item in items:
        name = item['Name']
        quantity = item['Quantity']
        price = item['Price']

        markup += f"[column: left > {name}; right * {quantity} \\[ {price} \\]]\n"

    markup += "[column: left - Pint; right * 1 \\[ \\]; indent 60]\nTable Number: NA\n[cut: feed; partial]\n[magnify: width 2; height 2]"

    # Post the markup to the target server
    headers = {
        'Content-Type': 'application/json',
        'Star-Api-Key': 'd17b8317-d6ef-4c0e-9c9b-c5a8592bf8fb'
    }
    response = requests.post('https://api.starprinter.online/v1/a/drinking/d/a0bc35c9/q', data=markup, headers=headers)

    # Return a response to the original request
    return 'OK'
