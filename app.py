from flask import Flask, render_template, request, redirect, url_for, session
import pymysql
from flask_mysqldb import MySQL
import pandas as pd
from sklearn import metrics 
import warnings
import pickle
from feature import FeatureExtraction
import numpy as np

app = Flask(__name__)
app.secret_key = 'ashok@123'

warnings.filterwarnings('ignore')

file = open("pickle/model.pkl","rb")
gbc = pickle.load(file)
file.close()

# Configure MySQL
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'test'

# mysql = MySQL(app).

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'test'
username1=""

def connect_to_database():
    return pymysql.connect(host=DB_HOST,
                           user=DB_USER,
                           password=DB_PASSWORD,
                           database=DB_NAME,
                           cursorclass=pymysql.cursors.DictCursor)

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        userDetails = request.form
        username = userDetails['username']
        password = userDetails['password']
        email = userDetails['email']
        mobile = userDetails['mobile']
        # Create cursor
        connection = connect_to_database()
        cursor = connection.cursor()
        # Execute query
        cursor.execute("INSERT INTO users(username,email,mobile, password) VALUES(%s, %s,%s,%s)", (username,email,mobile, password))
        # Commit to DB
        connection.commit()
        # Close connection
        cursor.close()
        return render_template('login.html')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        userDetails = request.form
        username = userDetails['username']
        password = userDetails['password']
        # Create cursor
        connection = connect_to_database()
        cursor = connection.cursor()
        # Execute query
        result =  cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))

        cursor.execute("SELECT username FROM users WHERE username = %s AND password = %s", (username, password))

        user_data = cursor.fetchone()

        username1 = user_data['username'] if user_data else None
        session['username'] = username1 
        
        if result > 0:
             return render_template('index.html', username=username1)
        else:
             return 'sorry ! something wrong'
        # Close connection
        cursor.close()
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove 'username' from session
    return redirect(url_for('home'))



@app.route('/index', methods=["GET", "POST"])
def index():
    if 'username' in session:
       username1 = session['username']
       if request.method == "POST":
           url = request.form["url"]
           obj = FeatureExtraction(url)
           x = np.array(obj.getFeaturesList()).reshape(1,30) 

           y_pred = gbc.predict(x)[0]
           # 1 is safe       
           # -1 is unsafe
           y_pro_phishing = gbc.predict_proba(x)[0,0]
           y_pro_non_phishing = gbc.predict_proba(x)[0,1]

           pred = "It is {0:.2f} %s safe to go ".format(y_pro_phishing*100)
        
           return render_template('index.html',username=username1, xx=round(y_pro_non_phishing,2), url=url)
    return render_template("index.html", xx=-1)

@app.route('/phishing',methods=['GET','POST'])
def phishing():
    if request.method == 'POST':
        # Get form data
        userDetails = request.form
        phishing = userDetails['phishing_url']
        genuine = userDetails['genuine_url']
        # email = userDetails['email']
        # mobile = userDetails['mobile']
        # Create cursor
        connection = connect_to_database()
        cursor = connection.cursor()
        # Execute query
        cursor.execute("INSERT INTO dataset(Phishing_URLs,Genuine_URLs) VALUES(%s,%s)", (phishing,genuine))
        # Commit to DB
        connection.commit()
        # Close connection
        cursor.close()
        return render_template('phishing.html')
    return render_template('phishing.html')


@app.route('/data',methods=['GET','POST'])
def data():
    connection = connect_to_database()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM dataset")  # Replace 'your_table_name' with your actual table name
        data = cursor.fetchall()  # Fetch all rows from the result

        # Close connection
        connection.close()

        return render_template('data.html', res=data)  # Pass the fetched data to the template for rendering
    except Exception as e:
        return f"An error occurred: {e}"
    

@app.route('/blog')
def blog():
    return render_template('blog.html')
    
@app.route('/About')
def About():
    return render_template('About.html')
    

if __name__ == '__main__':
    app.run(debug=True)
