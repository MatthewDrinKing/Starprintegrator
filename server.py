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
    path = data.get('path', 'v1/a/drinking/d/a0bc35c9/q')  # New line to extract the path from the JSON data
    api_key = data.get('api_key')  # New line to extract the API key from the JSON data

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
        'Star-Api-Key': api_key,
    }
    star_printer_response = requests.post(f'https://api.starprinter.online/{path}', data=markup, headers=headers)

    # Post the markup to the request catcher URL for debugging purposes
    headers = {
        'Content-Type': 'text/vnd.star.markup',
        'Star-Api-Key': api_key,  # Add API key to headers for request catcher
    }
    request_catcher_response = requests.post('https://testing-prod.requestcatcher.com/', data=markup, headers=headers)

    # Return a response to the original request
    return 'OK'
