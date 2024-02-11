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
    time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%H:%M')

    items = data.get('items', [{}])  # Updated to extract the list of items

    # Increment the order number
    order_number += 1

    # Generate the markup based on the extracted information
    markup = f"[magnify: width 1; height 1]\n"

    # Add order number and time
    markup += f"[column: left ORDER {order_number}; right Time {time}]\n"

    # Generate the markup for each item in the order
    for item in items:
        item_name = item.get('name', '')
        item_quantity = item.get('quantity', '')
        is_food = item.get('isfood', '').lower() == 'true'  # Convert to boolean

        # Determine the path based on is_food
        current_path = foodpath if is_food else path

        # Add the item markup to the overall markup with the correct path
        markup += f"[column: left {item_name}; right * {item_quantity}]\n"
        # Print the current path for debugging
        print(f'Current Path for {item_name}: {current_path}')

    markup += f"Table Number: {table_number}\n[cut: feed; partial]\n[magnify: width 1; height 1]"

    print('Generated markup:', markup)  # Print generated markup for debugging

    # Post the markup to the target server
    headers = {
        'Content-Type': 'text/vnd.star.markup',
        'Star-Api-Key': api_key,  # Include the API key in the headers
    }
    star_printer_response = requests.post(f'https://api.starprinter.online/{current_path}', data=markup, headers=headers)

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