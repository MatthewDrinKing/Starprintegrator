import requests
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

@app.route('/process-json', methods=['POST'])
def process_json():
    # Get the JSON data from the request
    data = request.get_json()

    # Extract the relevant information from the JSON data
    order_number = data.get('Order Number', '')
    time_str = data.get('Time', '')
    table_number = data.get('Table Number', 'NA')
    
    # Format the time string
    time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%H:%M')

    items = data.get('items', [])

    # Generate the markup based on the extracted information
    markup = f"[magnify: width 2; height 2]\n[column: left ORDER {order_number}; right Time {time}]\n"

    for item in items:
        name = item.get('name', '')
        quantity = item.get('quantity', '')
        price = item.get('price', '')

        markup += f"[column: left > {name}; right * {quantity} \\[ {price} \\]]\n"

    markup += f"Table Number: {table_number}\n[cut: feed; partial]\n[magnify: width 2; height 2]"

    # Post the markup to the target server
    headers = {
        'Content-Type': 'text/vnd.star.markup',
        'Star-Api-Key': 'd17b8317-d6ef-4c0e-9c9b-c5a8592bf8fb'
    }
    star_printer_response = requests.post('https://api.starprinter.online/v1/a/drinking/d/a0bc35c9/q', data=markup, headers=headers)

    # Post the markup to the request catcher URL for debugging purposes
    headers = {
        'Content-Type': 'text/vnd.star.markup',
    }
    request_catcher_response = requests.post('https://testing-prod.requestcatcher.com/', data=markup, headers=headers)

    # Return a response to the original request
    return 'OK'
