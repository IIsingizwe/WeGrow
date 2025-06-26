import os
import csv
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'wegrow-secret-key'

VALID_USERNAME = "admin"
VALID_PASSWORD = "password"

CHILD_FILE = 'data/children.csv'

def load_children():
    if not os.path.exists(CHILD_FILE):
        return []
    with open(CHILD_FILE, newline='') as csvfile:
        return list(csv.DictReader(csvfile))

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
            return redirect(url_for('children'))
        else:
            message = 'Invalid username or password. Please try again.'
    return render_template('login.html', message=message)

@app.route('/children')
def children():
    if 'logged_in' in session:
        children_data = load_children()
        return render_template('children.html', children=children_data, username=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

