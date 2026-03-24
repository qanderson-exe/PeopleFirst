from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

posts = []

@app.route('/')
def index():
    welcome_message = "Welcome to PeopleFirst!"
    return render_template('index.html', posts=posts, welcome=welcome_message)

@app.route('/create', methods=['POST'])
def create():
    title = request.form['title']
    content = request.form['content']

    if not title or not content:
        return redirect(url_for('index'))

    posts.append({
        'title': title,
        'content': content,
        'time': datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)