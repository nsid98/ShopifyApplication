from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
import sqlite3 as sql

UPLOAD_FOLDER = 'static/images/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_cursor():
    # This function will give us access to make changes to the database
    conn = sql.connect("database.db")
    cur = conn.cursor()
    return (cur, conn)

def initialize_db():
    (cur, conn) = get_cursor()

    # Initialize database with dummy values
    cur.execute("DROP TABLE IF EXISTS products")
    cur.execute("CREATE TABLE products (name TEXT, imgpath TEXT, price INTEGER, stock INTEGER)")
    cur.execute("INSERT INTO products VALUES ('Water Bottle', 'static/images/water_bottle.jpg', 10, 10)""")
    cur.execute("INSERT INTO products VALUES ('Swing', 'static/images/swing.jpg', 200, 10)""")
    cur.execute("INSERT INTO products VALUES ('Book', 'static/images/book.jpg', 5, 10)""")
    cur.execute("INSERT INTO products VALUES ('Apple', 'static/images/apple.jpg', 5, 10)")
        
    conn.commit()

@app.route("/")
def home_page():
    (cur, _) = get_cursor()
    cur.execute("SELECT rowid, * FROM products")
    
    # Get all the products from the products table and send them to index page
    rows = cur.fetchall()
    products = []
    for row in rows:
        products.append({
            "id":    row[0],
            "name":  row[1],
            "src":   "/%s" % (row[2]),
            "price": "$%.2f" % (row[3]/100.0),
            "stock": "%d remaining" % (row[4]),
        })

    return render_template("index.html", products=products)

@app.route("/", methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        # Save the image in static/images
        file=request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        (cur, conn) = get_cursor()
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']

        # Add the new product into the products table
        cur.execute("INSERT INTO products VALUES ( '" + name + "', '" + app.config['UPLOAD_FOLDER'] + filename+ "', " + price + ", " + stock + ")")
        conn.commit()
        return home_page()

@app.route("/buy/<product_id>")
def buy(product_id):

    (cur, conn) = get_cursor()

    cur.execute("SELECT rowid, price, stock FROM products WHERE rowid = ?", (product_id,))
    (rowid, price, stock) = cur.fetchone()
    
    if(stock == 1):
        cur.execute("DELETE FROM products WHERE rowid = " + product_id)
        conn.commit()
        return render_template("message.html", message="You got the last one!")

    cur.execute("UPDATE products SET stock = stock - 1 WHERE rowid = " + product_id)
    conn.commit()
    return render_template("message.html", message="You purchased your item!")

if __name__ == '__main__':
    initialize_db()
    app.run(debug=True)