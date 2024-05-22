import requests
from flask import Flask, request, jsonify
from datetime import datetime
import pytz

app = Flask(__name__)

order_number = 0  # Initialize the order number

@app.route('/process-json', methods=['POST'])
def process_json():
    global order_number  # Access the global order number variable

    try:
        # Get the JSON data from the request
        data = request.get_json()
        print('Received JSON data:', data)  # Print received JSON data for debugging

        # Extract the relevant information from the JSON data
        time_str = data.get('Time', '')
        timezone_str = data.get('timezone', 'UTC')  # Extract the timezone from the JSON data
        printer_width = int(data.get('printer_width', 58))  # Extract printer width, default to 58mm
        table_number = data.get('table_number', 'NA')
        path = data.get('path', 'v1/a/drinking/d/a0bc35c9/q')
        foodpath = data.get('foodpath', 'v1/a/drinking/d/a0bc35c9/q')
        api_key = data.get('api_key')

        # Convert time to local timezone
        utc_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        local_tz = pytz.timezone(timezone_str)
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
        formatted_time = local_time.strftime('%d %b %Y %I:%M%p')

        items = data.get('items', [{}])

        # Calculate grand total
        grand_total = sum(float(item.get('price', 0)) * float(item.get('quantity', 0)) for item in items)

        # Increment the order number
        order_number += 1

        # Adjust line length and text size based on printer width
        if printer_width == 80:
            line_length = 49
            header_dimension = 3
            body_dimension = 1.5
        else:  # Assume 58mm printer
            line_length = 30
            header_dimension = 2
            body_dimension = 1

        # Generate the markup based on the extracted information
        markup = (
            "[bold: on]\n"
            f"[magnify: width {header_dimension}; height {header_dimension}]\n"
            "DrinKing Order\n[negative: on]\n"
            f"Table number: {table_number if table_number.lower() != 'na' and table_number.strip() else 'Bar Pickup'}\n"
            "[space: count 1]\n[plain]\n[align: center]\n"
            f"[magnify: width {body_dimension}; height {body_dimension}]\n"
            f"Placed at {formatted_time}\n[upperline: on]\n"
            f"[space: count {line_length}]\n[plain]\n[plain]"
        )

        for item in items:
            name = item.get('name', '')
            quantity = item.get('quantity', '')
            price = item.get('price', '')
            markup += f"\n[column: left {quantity} * {name}; right {float(price) * float(quantity)}]"

        markup += (
            f"\n{'-' * line_length}\n"
            f"[column: left Total; right {grand_total}]\n"
            f"{'-' * line_length}\n"
            "[align: left]\n[cut: feed; partial]"
        )

        print('Generated markup:', markup)  # Print generated markup for debugging

        # Post the markup to the target server
        headers = {
            'Content-Type': 'text/vnd.star.markup',
            'Star-Api-Key': api_key,  # Include the API key in the headers
        }
        star_printer_response = requests.post(f'https://api.starprinter.online/{path}', data=markup, headers=headers)
        
        if star_printer_response.status_code != 200:
            return jsonify({"error": "Failed to send to star printer", "details": star_printer_response.text}), 500

        # Post the markup to the request catcher URL for debugging purposes
        request_catcher_response = requests.post('https://testing-prod.requestcatcher.com/', data=markup, headers=headers)
        
        if request_catcher_response.status_code != 200:
            return jsonify({"error": "Failed to send to request catcher", "details": request_catcher_response.text}), 500

        # Return a response to the original request
        return 'OK'

    except Exception as e:
        print('Error processing request:', e)
        return jsonify({"error": "Failed to process request", "details": str(e)}), 500

@app.route('/', methods=['GET'])  # Add a default route for the root path
def default_route():
    return 'Welcome to the Starprintegrator server'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)