import os
import csv
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'wegrow-secret-key'

CHILD_FILE = 'data/children.csv'
HOSPITAL_FILE = 'data/hospital_children.csv'

VALID_USERNAME = "admin"
VALID_PASSWORD = "password"

def load_children():
    if not os.path.exists(CHILD_FILE):
        return []
    with open(CHILD_FILE, newline='') as csvfile:
        return list(csv.DictReader(csvfile))

def save_child(data):
    file_exists = os.path.exists(CHILD_FILE)
    with open(CHILD_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def child_exists(child_id, month):
    children = load_children()
    return any(c['ChildID'] == child_id and c['Month'] == month for c in children)

@app.route('/home')
def home():
    if 'logged_in' in session:
        return f"Welcome, {session['username']}!"
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            message = 'Both username and password are required.'
        elif username == VALID_USERNAME and password == VALID_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('home'))
        else:
            message = 'Invalid username or password. Please try again.'

    return render_template('login.html', message=message)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    if request.method == 'POST':
        form = request.form
        if child_exists(form['child_id'], form['month']):
            message = 'Child already exists in system for that month.'
        else:
            data = {
                'ChildID': form['child_id'],
                'Name': form['name'],
                'District': form['district'],
                'Birthdate': form['birthdate'],
                'Month': form['month'],
                'Height': form['height'],
                'Weight': form['weight'],
                'Age': form['age'],
                'Status': 'Stunted',
                'ParentNames': form['parent_names'],
                'ParentID': form['parent_id'],
                'Sector': form['sector'],
                'Cell': form['cell'],
                'Village': form['village'],
                'Hidden': 'False'
            }
            save_child(data)
            message = 'Child registered successfully.'
    return render_template('index.html', message=message)

@app.route('/get-child-details/<child_id>')
def get_child_details(child_id):
    if not os.path.exists(HOSPITAL_FILE):
        return jsonify({})
    with open(HOSPITAL_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ChildID'] == child_id:
                return jsonify({
                    'Name': row['Name'],
                    'District': row['District'],
                    'Birthdate': row['Birthdate']
                })
    return jsonify({})

@app.route('/records')
def records():
    children = load_children()
    return render_template('records.html', children=children)

@app.route('/delete/<child_id>/<month>')
def delete(child_id, month):
    children = load_children()
    updated = [c for c in children if not (c['ChildID'] == child_id and c['Month'] == month)]
    with open(CHILD_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=updated[0].keys() if updated else [])
        if updated:
            writer.writeheader()
            writer.writerows(updated)
    return redirect(url_for('records'))

@app.route('/toggle-hide/<child_id>/<month>')
def toggle_hide(child_id, month):
    children = load_children()
    for c in children:
        if c['ChildID'] == child_id and c['Month'] == month:
            c['Hidden'] = 'False' if c.get('Hidden') == 'True' else 'True'
    with open(CHILD_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=children[0].keys())
        writer.writeheader()
        writer.writerows(children)
    return redirect(url_for('records'))

@app.route('/toggle-status/<child_id>/<month>')
def toggle_status(child_id, month):
    children = load_children()
    for c in children:
        if c['ChildID'] == child_id and c['Month'] == month:
            c['Status'] = 'Not Stunted' if c['Status'] == 'Stunted' else 'Stunted'
    with open(CHILD_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=children[0].keys())
        writer.writeheader()
        writer.writerows(children)
    return redirect(url_for('records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
