from flask import Flask, render_template, request, redirect, url_for
import sqlite3

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
    
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Redirect to the dashboard without verifying credentials
        # That will be the microservice a teammate makes
        return redirect(url_for('dashboard'))
    return render_template('login.html')

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
        status = request.form['status']
        total_acres = request.form['total_acres']
        containment_percentage = request.form['containment_percentage']
        total_ppl = request.form['total_ppl']
        crew = request.form['crew']
        engines = request.form['engines']
        helicopters = request.form['helicopters']

        conn = sqlite3.connect('incidents.db')
        cursor = conn.cursor()
        
        # Inserts a new record into incident_history to track the changes
        cursor.execute('''
            INSERT INTO incidents (name, status, total_acres, containment_percentage, total_ppl, crew, engines, helicopters)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, status, total_acres, containment_percentage, total_ppl, crew, engines, helicopters))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('create_incident.html')

# Route for assign button
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

# Route for update button
@app.route('/update/<int:incident_id>', methods=['GET', 'POST'])
def update_incident(incident_id):
    conn = sqlite3.connect('incidents.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Get new values from the form submission
        total_acres = request.form['total_acres']
        containment_percentage = request.form['containment_percentage']
        structures_lost = request.form['structures_lost']
        cost_to_date = request.form['cost_to_date']
        date = request.form['date']
        update_description = request.form.get('update_description', '')
        
        # Update the main incidents table with the latest values
        cursor.execute('''
            UPDATE incidents
            SET total_acres = ?, containment_percentage = ?, structures_lost = ?, cost_to_date = ?
            WHERE id = ?
        ''', (total_acres, containment_percentage, structures_lost, cost_to_date, incident_id))
        
        # Insert a new record into history to track the changes
        cursor.execute('''
            INSERT INTO incident_history (incident_id, date, total_acres, containment_percentage, structures_lost, cost_to_date, update_description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (incident_id, date, total_acres, containment_percentage, structures_lost, cost_to_date, update_description))
        
        conn.commit()
        conn.close()
        
        # Redirect back to the dashboard
        return redirect(url_for('dashboard'))
    
    # Fetch current values for the incident
    cursor.execute("SELECT name, total_acres, containment_percentage, structures_lost, cost_to_date FROM incidents WHERE id = ?", (incident_id,))
    incident = cursor.fetchone()
    conn.close()
    
    # Pass both the incident data and incident_id to the template
    return render_template('update_incident.html', incident=incident, incident_id=incident_id)

# Route for incident summary when clicking on an incident
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

    # Fetch the incident history for displaying in the chart
    cursor.execute("SELECT date, total_acres, containment_percentage, structures_lost, cost_to_date FROM incident_history WHERE incident_id = ? ORDER BY date ASC", (incident_id,))
    history = cursor.fetchall()
    
    conn.close()
    return render_template('incident_summary.html', incident=incident, latest_description=latest_description, history=history)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
