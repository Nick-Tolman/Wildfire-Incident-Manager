from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = '9f5f0569561080074398a1f580abb5af' 

@app.route('/weather', methods=['POST'])
def get_weather():
    data = request.get_json()
    lat = data.get('latitude')
    lon = data.get('longitude')

    if not lat or not lon:
        return jsonify({"error": "Latitude and Longitude are required"}), 400

    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        temperature_kelvin = weather_data['main']['temp']
        temperature_fahrenheit = (temperature_kelvin - 273.15) * 9/5 + 32
        wind_speed = weather_data['wind']['speed'] 
        humidity = weather_data['main']['humidity'] 
        return jsonify({
            "temperature": round(temperature_fahrenheit, 2),
            "wind_speed": wind_speed,
            "humidity": humidity,
            "weather": weather_data['weather'][0]['description']
    })

    else:
        return jsonify({"error": "Unable to fetch weather data"}), 500
    
if __name__ == '__main__':
    app.run(port=5001, debug=True)
