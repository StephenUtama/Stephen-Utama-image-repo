from flask import Flask, render_template, g
import sqlite3 as sql

app = Flask(__name__)

DATABASE = 'database.db'

def get_db():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sql.connect(DATABASE)
    cur = conn.cursor()
    return (cur, conn)

@app.teardown_appcontext
def close_connection(exception):
    conn = getattr(g, '_database', None)
    if conn is not None:
        conn.close()

"""Initialize the sqlite database and fill up the `products` table with sample data."""
def initialize_db():
    with app.app_context():
        (cur, conn) = get_db()

        cur.execute("DROP TABLE IF EXISTS products")
        cur.execute("CREATE TABLE products (name TEXT, imgpath TEXT, price INTEGER, stock INTEGER)")
        cur.execute("""INSERT INTO products (name, imgpath, price, stock) VALUES \
            ('Sunset Portrait', 'images/sunset.jpg', 120, 3), \
            ('StarryNight Portrait', 'images/starrynight.jpg', 270, 2)
        """)

        cur.execute("DROP TABLE IF EXISTS transactions")
        cur.execute("CREATE TABLE transactions (timestamp TEXT, productid INTEGER, value INTEGER)")
        
        cur.execute("DROP TABLE IF EXISTS discount")
        cur.execute("CREATE TABLE discount (activated INTEGER)")
        cur.execute("""INSERT INTO discount (activated) VALUES \
            (0)""")

        conn.commit()

@app.route("/")
def home_page():
    (cur, _) = get_db()
    cur.execute("SELECT rowid, * FROM products")
    
    rows = cur.fetchall()
    print("Retrieved %d database entries" % len(rows))
    
    products = []
    for row in rows:
        products.append({
            "id":    row[0],
            "name":  row[1],
            "src":   "/static/%s" % (row[2]),
            "price": "$%.2f" % (row[3]),
            "stock": "%d left" % (row[4]),
        })
    
    cur.execute("SELECT SUM(value) FROM transactions")
    result = cur.fetchone()[0]
    earnings = result if result else 0

    return render_template("index.html", products=products, earnings=earnings)

@app.route("/buy/<product_id>", methods=['GET'])
def buy(product_id):

    (cur, conn) = get_db()

    cur.execute("SELECT rowid, price, stock FROM products WHERE rowid = ?", (product_id,))
    result = cur.fetchone()

    if not result:
        return render_template("message.html", message="Invalid product ID!"), 404
    (rowid, price, stock) = result

    if stock <= 0:
        return render_template("message.html", message="Insufficient stock!")

    cur.execute("INSERT INTO transactions (timestamp, productid, value) VALUES " + \
        "(datetime(), ?, ?)", (rowid, price))

    cur.execute("UPDATE products SET stock = stock - 1 WHERE rowid = ?", (product_id,))
    conn.commit()
    return render_template("message.html", message="Purchase successful!")
    

@app.route("/discount")
def discount():
    (cur, conn) = get_db()

    cur.execute("SELECT activated FROM discount")
    (active ,) = cur.fetchone()

    print(active)

    activated_message = "Discount activated!"

    

    if active == 0:
        cur.execute("UPDATE discount SET activated = 1")
        cur.execute("UPDATE products SET price = .90 * price")
    else:
        activated_message = "Discount has already been activated!"


    conn.commit()

    return render_template("message.html", message=activated_message)

if __name__ == '__main__':
    initialize_db()
    app.run(debug = True)