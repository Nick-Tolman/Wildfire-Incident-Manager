from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/fire_danger', methods=['POST'])
def calculate_fire_danger():
    data = request.get_json()
    temperature = data.get('temperature')
    wind_speed = data.get('wind_speed')
    humidity = data.get('humidity')

    if not all([temperature is not None, wind_speed is not None, humidity is not None]):
        return jsonify({"error": "Temperature, wind speed, and humidity are required"}), 400

    danger_rating = (temperature * 0.6) + (wind_speed * 0.3) - (humidity * 0.1)
    danger_level = "Low"
    if danger_rating > 50:
        danger_level = "High"
    elif danger_rating > 30:
        danger_level = "Moderate"

    return jsonify({
        "fire_danger_score": round(danger_rating, 2),
        "fire_danger_level": danger_level
    })

if __name__ == '__main__':
    app.run(port=5002, debug=True)
