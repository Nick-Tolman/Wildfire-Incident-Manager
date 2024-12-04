import sqlite3
import random
from datetime import datetime, timedelta

# Generate random latitude and longitude within Oregon's bounds
def generate_lat_long():
    # Approximate bounds for Oregon, USA
    lat = round(random.uniform(42.0, 46.3), 6)  # Latitude range
    long = round(random.uniform(-124.6, -116.5), 6)  # Longitude range
    return lat, long

# Generate a random date in August of the current year
def generate_august_date():
    year = datetime.now().year
    day = random.randint(1, 31)  # August has 31 days
    return datetime(year, 8, day)

# Script to populate the database
def populate_database():
    # Connect to the database
    conn = sqlite3.connect('incidents.db')
    cursor = conn.cursor()
    
    # Create 20 incidents
    for i in range(1, 21):
        name = f"Incident {i}"
        lat, long = generate_lat_long()  # Generate random latitude and longitude
        status = "Closed" if i <= 6 else "Open"  # Mark first 6 incidents as "Closed"
        total_acres = random.randint(100, 20000)
        containment_percentage = random.randint(0, 100)
        total_ppl = random.randint(10, 500)
        crew = random.randint(1, 35)
        engines = random.randint(0, 20)
        helicopters = random.randint(0, 10)
        structures_lost = random.randint(0, 5)
        cost_to_date = round(random.uniform(100000, 10000000), 2)
        
        # Generate a random start date in August
        start_date = generate_august_date()
        start_date_str = start_date.strftime("%Y-%m-%d")
        
        # Insert incident data into the incidents table
        cursor.execute('''
            INSERT INTO incidents (
                name, lat, long, status, total_acres, containment_percentage, 
                total_ppl, crew, engines, helicopters, structures_lost, 
                cost_to_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, lat, long, status, total_acres, containment_percentage, 
              total_ppl, crew, engines, helicopters, structures_lost, cost_to_date))
        
        incident_id = cursor.lastrowid

        # Generate historical data for the incident
        for j in range(random.randint(3, 10)):
            # Add random days (up to 5) to the start date, ensuring it stays within August
            history_date = start_date + timedelta(days=j * random.randint(1, 5))
            if history_date.month != 8:
                break
            history_date_str = history_date.strftime("%Y-%m-%d")
            acres = max(total_acres - random.randint(0, total_acres // 10), 0)
            containment = min(containment_percentage + random.randint(0, 10), 100)
            ppl = max(total_ppl - random.randint(0, total_ppl // 10), 0)
            cost = cost_to_date + random.uniform(0, 10000)
            
            # Insert historical data into the incident_history table
            cursor.execute('''
                INSERT INTO incident_history (
                    incident_id, date, total_acres, containment_percentage,
                    total_ppl, crew, engines, helicopters, cost_to_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (incident_id, history_date_str, acres, containment, ppl, crew, engines, helicopters, cost))

    conn.commit()
    conn.close()
    print("Database populated with 20 incidents and historical data for August.")

populate_database()
