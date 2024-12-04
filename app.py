from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests

app = Flask(__name__)

# Initialize or update the database
def init_db():
    conn = sqlite3.connect('incidents.db')
    cursor = conn.cursor()
    
    # Create incidents table with necessary columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            lat REAL,
            long REAL,
            status TEXT NOT NULL,
            total_acres INTEGER,
            containment_percentage INTEGER,
            total_ppl INTEGER,
            crew INTEGER,
            engines INTEGER,
            helicopters INTEGER,
            structures_lost INTEGER,
            cost_to_date REAL
        )
    ''')
    
    # Table for tracking history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incident_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER,
            date TEXT,
            lat REAL,
            long REAL,
            total_ppl INTEGER,
            crew INTEGER,
            engines INTEGER,
            helicopters INTEGER,
            total_acres INTEGER,
            containment_percentage INTEGER,
            structures_lost INTEGER,
            cost_to_date REAL,
            update_description TEXT,
            FOREIGN KEY (incident_id) REFERENCES incidents(id)
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login_page.html')

@app.route('/logout', methods=['GET'])
def logout():
    return redirect(url_for('login_page'))

# Route for the Dashboard
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('incidents.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, status, total_acres, containment_percentage, total_ppl, crew, engines, helicopters, cost_to_date FROM incidents")
    incidents = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', incidents=incidents)

# Route for creating a new incident
@app.route('/create-incident', methods=['GET', 'POST'])
def create_incident():
    if request.method == 'POST':
        name = request.form['name']
        lat = request.form['lat']
        long = request.form['long']
        status = request.form['status']
        total_acres = request.form['total_acres']
        containment_percentage = request.form['containment_percentage']
        total_ppl = request.form['total_ppl']
        crew = request.form['crew']
        engines = request.form['engines']
        helicopters = request.form['helicopters']

        conn = sqlite3.connect('incidents.db')
        cursor = conn.cursor()
        
        # Insert a new record into incident_history to track the changes
        cursor.execute('''
            INSERT INTO incidents (name, lat, long, status, total_acres, containment_percentage, total_ppl, crew, engines, helicopters)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, lat, long, status, total_acres, containment_percentage, total_ppl, crew, engines, helicopters))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('create_incident.html')

# assgin button route
@app.route('/assign/<int:incident_id>', methods=['GET', 'POST'])
def assign_responders(incident_id):
    conn = sqlite3.connect('incidents.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Get new values from the form submission
        total_ppl = request.form['total_ppl']
        crew = request.form['crew']
        engines = request.form['engines']
        helicopters = request.form['helicopters']
        date = request.form['date']
        
        # Update the main incidents table with the latest values
        cursor.execute('''
            UPDATE incidents
            SET total_ppl = ?, crew = ?, engines = ?, helicopters = ?
            WHERE id = ?
        ''', (total_ppl, crew, engines, helicopters, incident_id))
        
        # Insert a new record into incident_history to track the changes
        cursor.execute('''
            INSERT INTO incident_history (incident_id, date, total_ppl, crew, engines, helicopters)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (incident_id, date, total_ppl, crew, engines, helicopters))
        
        conn.commit()
        conn.close()
        
        # Redirect back to the dashboard
        return redirect(url_for('dashboard'))
    
    # Fetch current values for the incident
    cursor.execute("SELECT name, total_ppl, crew, engines, helicopters FROM incidents WHERE id = ?", (incident_id,))
    incident = cursor.fetchone()
    conn.close()
    
    # Pass both the incident data and incident_id to the template
    return render_template('assign_responders.html', incident=incident, incident_id=incident_id)

# update button route
@app.route('/update/<int:incident_id>', methods=['GET', 'POST'])
def update_incident(incident_id):
    conn = sqlite3.connect('incidents.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Get new values from the form submission
        total_acres = request.form['total_acres']
        lat = request.form['lat']
        long = request.form['long']
        containment_percentage = request.form['containment_percentage']
        structures_lost = request.form['structures_lost']
        cost_to_date = request.form['cost_to_date']
        date = request.form['date']
        update_description = request.form.get('update_description', '')
        
        # Update the main incidents table with the latest values
        cursor.execute('''
            UPDATE incidents
            SET total_acres = ?, lat = ?, long = ?, containment_percentage = ?, structures_lost = ?, cost_to_date = ?
            WHERE id = ?
        ''', (total_acres, lat, long, containment_percentage, structures_lost, cost_to_date, incident_id))
        
        # Insert a new record into history to track the changes
        cursor.execute('''
            INSERT INTO incident_history (incident_id, date, lat, long, total_acres, containment_percentage, structures_lost, cost_to_date, update_description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (incident_id, date, lat, long, total_acres, containment_percentage, structures_lost, cost_to_date, update_description))
        
        conn.commit()
        conn.close()
        
        # Redirect back to the dashboard
        return redirect(url_for('dashboard'))
    
    # Fetch current values for the incident
    cursor.execute("SELECT name, lat, long, total_acres, containment_percentage, structures_lost, cost_to_date FROM incidents WHERE id = ?", (incident_id,))
    incident = cursor.fetchone()
    conn.close()
    
    # Pass both the incident data and incident_id to the template
    return render_template('update_incident.html', incident=incident, incident_id=incident_id)

@app.route('/incident/<int:incident_id>')
def incident_summary(incident_id):
    conn = sqlite3.connect('incidents.db')
    cursor = conn.cursor()
    
    # Fetch the main incident details
    cursor.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
    incident = cursor.fetchone()
    
    # Fetch the latest update description (if applicable)
    cursor.execute("SELECT update_description FROM incident_history WHERE incident_id = ? ORDER BY date DESC LIMIT 1", (incident_id,))
    latest_description = cursor.fetchone()
    latest_description = latest_description[0] if latest_description else "No updates available."

    # Fetch the latest date from incident history
    cursor.execute("SELECT date FROM incident_history WHERE incident_id = ? ORDER BY date DESC LIMIT 1", (incident_id,))
    latest_date = cursor.fetchone()
    latest_date = latest_date[0] if latest_date else None

    # Fetch incident's latitude and longitude
    cursor.execute("SELECT lat, long FROM incidents WHERE id = ?", (incident_id,))
    incident_location = cursor.fetchone()

    # Fetch the incident history for displaying in the chart
    cursor.execute("SELECT date, total_acres, containment_percentage, structures_lost, cost_to_date FROM incident_history WHERE incident_id = ? ORDER BY date ASC", (incident_id,))
    history = cursor.fetchall()
    
    conn.close()
    return render_template(
        'incident_summary.html', 
        incident_location=incident_location, 
        incident=incident, 
        latest_description=latest_description, 
        latest_date=latest_date,
        history=history
        )

@app.route('/stats')
def stats_page():
    response = requests.get('http://127.0.0.1:5003/generate_graphs')
    if response.status_code == 200:
        graph_paths = response.json()
        return render_template('stats.html', graphs=graph_paths)
    else:
        return "Error fetching graphs from stats service", 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
