import os
import time
import pymysql
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Mengambil konfigurasi dari Environment Variables
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'rootpassword')
DB_NAME = os.environ.get('DB_NAME', 'crud_db')

def get_db_connection():
    retries = 10
    while retries > 0:
        try:
            connection = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except pymysql.MySQLError:
            retries -= 1
            time.sleep(2)
    raise Exception("Gagal terhubung ke Database MariaDB/MySQL")

def init_db():
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
            cursor.execute(f"USE {DB_NAME};")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nama VARCHAR(100) NOT NULL,
                    jumlah INT NOT NULL,
                    harga DECIMAL(10,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error Init DB: {e}")

# READ
@app.route('/')
def index():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM items ORDER BY id DESC")
        items = cursor.fetchall()
    conn.close()
    hostname = os.uname().nodename
    return render_template('index.html', items=items, container_id=hostname)

# CREATE
@app.route('/add', methods=['POST'])
def add_item():
    nama = request.form['nama']
    jumlah = request.form['jumlah']
    harga = request.form['harga']
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO items (nama, jumlah, harga) VALUES (%s, %s, %s)", (nama, jumlah, harga))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# UPDATE
@app.route('/update/<int:id>', methods=['POST'])
def update_item(id):
    nama = request.form['nama']
    jumlah = request.form['jumlah']
    harga = request.form['harga']
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE items SET nama=%s, jumlah=%s, harga=%s WHERE id=%s", (nama, jumlah, harga, id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# DELETE
@app.route('/delete/<int:id>', methods=['GET'])
def delete_item(id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM items WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)