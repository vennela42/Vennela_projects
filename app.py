from flask import Flask, request, redirect, url_for, render_template, session, flash
import os
import mysql.connector
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Photo upload settings
app.config['UPLOAD_FOLDER'] = 'static/Uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Vennelahari@28',
        database='platform'
    )

@app.route('/')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['username'] = user[1]  # Assuming 1 is the index for username
            session['user_id'] = user[0]   # Assuming 0 is the index for user_id
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blogs")
    blogs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard.html', data=blogs)

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO blogs (user_id, title, content, photo_filename) VALUES (%s, %s, %s, %s)",
                           (session['user_id'], title, content, filename))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('dashboard'))

    return render_template('add_post.html')

@app.route('/edit_post/<int:blog_id>', methods=['GET', 'POST'])
def edit_post(blog_id):
    

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor.execute("UPDATE blogs SET title = %s, content = %s WHERE id = %s", (title, content, blog_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard'))
    cursor.execute("SELECT * FROM blogs WHERE id = %s", (blog_id,))
    blog = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_posts.html', data=blog)

@app.route('/view_post/<int:blog_id>', methods=['GET', 'POST'])
def view_post(blog_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM blogs WHERE id = %s', (blog_id,))
    blog = cursor.fetchone()

    cursor.execute('SELECT comments.comment, comments.created_at, users.username FROM comments JOIN users ON comments.user_id = users.id WHERE blog_id = %s', (blog_id,))
    comments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('view_post.html', blog=blog, comments=comments)

@app.route('/add_comment/<int:blog_id>/comment', methods=['POST'])
def add_comment(blog_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    comment_text = request.form['comment']
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO comments (blog_id, user_id, comment) VALUES (%s, %s, %s)', (blog_id, user_id, comment_text))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('view_post', blog_id=blog_id))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))
@app.route('/delete_post/<int:blog_id>', methods=['POST'])
def delete_post(blog_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute the delete statement
    cursor.execute("DELETE FROM blogs WHERE id = %s", (blog_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=False)
