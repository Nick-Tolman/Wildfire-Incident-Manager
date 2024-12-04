import sqlite3
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from flask import Flask, jsonify
from datetime import datetime
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

GRAPH_DIR = 'static/graphs'
os.makedirs(GRAPH_DIR, exist_ok=True)

def generate_graphs(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Generate Cumulative Acres Burned Each Day 
    cursor.execute("""
        SELECT date, SUM(total_acres) OVER (ORDER BY date) AS cumulative_acres
        FROM incident_history
        ORDER BY date
    """)
    acres_data = cursor.fetchall()

    # Parse dates into datetime objects
    dates = [datetime.strptime(row[0], "%Y-%m-%d") for row in acres_data]
    cumulative_acres = [row[1] for row in acres_data]

    # Plot Cumulative Acres Burned Each Day
    plt.figure(figsize=(10, 6))
    plt.plot(dates, cumulative_acres, marker='o', color='orange')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Acres Burned')
    plt.title('Cumulative Acres Burned Each Day')
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    cumulative_graph_path = os.path.join(GRAPH_DIR, 'cumulative_acres_burned.png')
    plt.savefig(cumulative_graph_path)
    plt.close()

    # Generate Average Containment Percentage Each Day 
    cursor.execute("""
        SELECT date, AVG(containment_percentage)
        FROM incident_history
        GROUP BY date
        ORDER BY date
    """)
    containment_data = cursor.fetchall()

    if containment_data:
        containment_dates = [datetime.strptime(row[0], "%Y-%m-%d") for row in containment_data]
        avg_containment = [row[1] for row in containment_data]
        plt.figure(figsize=(10, 6))
        plt.plot(containment_dates, avg_containment, marker='o', color='green')
        plt.xlabel('Date')
        plt.ylabel('Average Containment Percentage')
        plt.title('Average Containment Percentage Each Day')
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        containment_graph_path = os.path.join(GRAPH_DIR, 'avg_containment.png')
        plt.savefig(containment_graph_path)
        plt.close()
    else:
        containment_graph_path = None
        print("No containment data available.")

    # Generate Total Cost to Date Graph 
    cursor.execute("""
        SELECT date, SUM(cost_to_date) OVER (ORDER BY date) AS total_cost
        FROM incident_history
        ORDER BY date
    """)
    cost_data = cursor.fetchall()

    if cost_data:
        cost_dates = [datetime.strptime(row[0], "%Y-%m-%d") for row in cost_data]
        total_cost = [row[1] / 1_000_000 for row in cost_data]  # Convert cost to millions

        # Plot Total Cost to Date
        plt.figure(figsize=(10, 6))
        plt.plot(cost_dates, total_cost, marker='o', color='blue')
        plt.xlabel('Date')
        plt.ylabel('Total Cost to Date (Millions USD)')
        plt.title('Total Cost to Date Over Time')
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        cost_graph_path = os.path.join(GRAPH_DIR, 'total_cost_to_date.png')
        plt.savefig(cost_graph_path)
        plt.close()
    else:
        cost_graph_path = None
        print("No cost data available.")


    conn.close()

    return {
        'cumulative_acres_burned': cumulative_graph_path,
        'avg_containment': containment_graph_path,
        'total_cost_to_date': cost_graph_path
    }


@app.route('/generate_graphs', methods=['GET'])
def generate_graphs_endpoint():
    database_path = 'incidents.db'
    graph_paths = generate_graphs(database_path)
    return jsonify(graph_paths)

if __name__ == '__main__':
    app.run(port=5003, debug=True)
