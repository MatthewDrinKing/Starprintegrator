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
    print('Received JSON data:', data)  # Print received JSON data for debugging

    # Extract the relevant information from the JSON data
    time_str = data.get('Time', '')
    table_number = data.get('table_number', 'NA')
    path = data.get('path', 'v1/a/drinking/d/a0bc35c9/q')  # New line to extract the path from the JSON data
    foodpath = data.get('foodpath', 'v1/a/drinking/d/a0bc35c9/q')  # New line to extract the foodpath from the JSON data
    api_key = data.get('api_key')  # Extract the API key from the JSON data

    # Format the time string
    time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d %b %Y %I:%M%p')

    items = data.get('items', [{}])  # Updated to extract the list of items

    # Calculate grand total
    grand_total = sum(float(item.get('price', 0)) * float(item.get('quantity', 0)) for item in items)

    # Increment the order number
    order_number += 1

    # Generate the markup based on the extracted information
    markup = f"[bold: on]\n[magnify: width 3; height 3]\nDrinKing Order\n[negative: on]\nTable number: {table_number if table_number.lower() != 'na' and table_number.strip() else 'Bar Pickup'}\n[space: count 1]\n[plain]\n[align: center]\n[magnify: width 1; height 1]\nPlaced at {time}\n[upperline: on]\n[space: count 48]\n[plain]\n[plain]"

    for item in items:
        name = item.get('name', '')
        quantity = item.get('quantity', '')
        price = item.get('price', '')
        markup += f"\n[column: left {quantity} * {name}; right {float(price) * float(quantity)}]"

    markup += f"\n------------------------------------------------\n[column: left Total; right *{grand_total}]\n------------------------------------------------\n[align: left]\n[cut: feed; partial]"
    print('Generated markup:', markup)  # Print generated markup for debugging

    # Post the markup to the target server
    headers = {
        'Content-Type': 'text/vnd.star.markup',
        'Star-Api-Key': api_key,  # Include the API key in the headers
    }
    star_printer_response = requests.post(f'https://api.starprinter.online/{path}', data=markup, headers=headers)

    # Post the markup to the request catcher URL for debugging purposes
    headers = {
        'Content-Type': 'text/vnd.star.markup',
    }
    request_catcher_response = requests.post('https://testing-prod.requestcatcher.com/', data=markup, headers=headers)

    # Return a response to the original request
    return 'OK'

@app.route('/', methods=['GET'])  # Add a default route for the root path
def default_route():
    return 'Welcome to the Starprintegrator server'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)