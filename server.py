import requests
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

order_number = 0  # Initialize the order number

@app.route('/process-json', methods=['POST'])
def process_json():
    global order_number  # Access the global order number variable

    # Get the JSON data from the request
    data = request.get_json()

    # Extract the relevant information from the JSON data
    time_str = data.get('Time', '')
    table_number = data.get('table_number', 'NA') if 'table_number' in data else 'NA'
    path = data.get('path', 'v1/a/drinking/d/a0bc35c9/q')  # New line to extract the path from the JSON data
    api_key = data.get('api_key')  # New line to extract the API key from the JSON data

    # Format the time string
    time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%H:%M')

    items = data.get('name', [{}])[0]  # Updated to extract the first item from the 'name' list

    # Increment the order number
    order_number += 1

    # Generate the markup based on the extracted information
    markup = f"[magnify: width 2; height 2]\n[column: left ORDER {order_number}; right Time {time}]\n"

    name = items.get('name', '')
    quantity = items.get('quantity', '')
    price = items.get('price', '')

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

@app.route('/', methods=['GET'])  # Add a default route for the root path
def default_route():
    return 'Welcome to the Starprintegrator server'

if __name__ == '__main__':
    app.run(port=5000)  # Set the desired port number here
