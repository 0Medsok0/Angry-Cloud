from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tours.db'
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(50))
    date = db.Column(db.Date)
    price = db.Column(db.Float)
    type = db.Column(db.String(50))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
# @login_required
def index():
    if current_user.is_authenticated:
        tours = Tour.query.all()
        return render_template('index.html', tours=tours)
    else:
        return redirect(url_for('login'))


@app.route('/book/<int:tour_id>')
@login_required
def book(tour_id):
    tour = Tour.query.get(tour_id)
    booking = Booking(user_id=current_user.id, tour_id=tour_id)
    db.session.add(booking)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Добавляем туры
@app.route('/add_tour', methods=['GET', 'POST'])
@login_required
def add_tour():
    if request.method == 'POST':
        destination = request.form['destination']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        price = request.form['price']
        type = request.form['type']
        tour = Tour(destination=destination, date=date, price=price, type=type)
        db.session.add(tour)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_tour.html')



if __name__ == '__main__':
    with app.app_context():
        # Создаем базу данных и таблицу туров
        db.create_all()
    app.run(debug=True)
