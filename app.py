from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(60), nullable=False)
    lastname = db.Column(db.String(60), nullable=False)
    username = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

with app.app_context():
    db.create_all()

def check_emailDuplicates(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return True
    else:
        return False

def validate(email,password, confirm_password):
    if len(password) < 8:
        return False, ["Password should be at least 8 characters long."]
    if not (any(c.islower() for c in password) and any(c.isupper() for c in password) and password[-1].isdigit()):
        return False, ["Password must contain at least one lowercase letter, one uppercase letter and end with a number."]
    if password != confirm_password:
        return False, ["Passwords do not match."]
    if not email:
        return False, ["Email is required."]
    elif check_emailDuplicates(email):
        return False, ["Email already exists."]
    return True, []

@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('login'))


@app.route('/dbshow', methods=['GET', 'POST'])
def dbshow():
    rows = User.query.all()
    return render_template('db.html', rows=rows)


@app.route('/thankyou', methods=['GET'])
def thankyou():
    return render_template('thankyou.html')

@app.route('/secretPage', methods=['GET'],defaults={'username': None})
def secretPage(username):
    if username:
        return render_template('secretPage.html', username=username)
    else:
        return render_template('login.html', error="Please login first")

@app.route('/login', methods=['GET', 'POST'],defaults={'error': None})
def login(error):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            return render_template('secretPage.html', username=username)
        else:
            return render_template('login.html', error="Invalid username or password")
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'],defaults={'success': False, 'messages': []})
def signup(success, messages):
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        success, messages = validate(email,password, confirm_password)
        if not success:
            return render_template('signup.html', messages=messages)
        else:
            user = User(firstname=firstname, lastname=lastname, username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('thankyou'))
    print("Signup=>", success, messages)
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
