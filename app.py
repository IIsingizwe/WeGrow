import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            return redirect(url_for('children'))
        else:
            return render_template('login.html', message="Invalid credentials")
    return render_template('login.html')

@app.route('/children')
def children():
    return render_template('children.html')

@app.route('/add-child', methods=['POST'])
def add_child():
    return redirect(url_for('children'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
