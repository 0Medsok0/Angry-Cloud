from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tours.db'
db = SQLAlchemy(app)

# Создаем модель туров в базе данных
class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    includes = db.Column(db.Text, nullable=False)
    spots = db.Column(db.Integer, nullable=False)

@app.route('/')
def index():
    tours = Tour.query.all()
    return render_template('index.html', tours=tours)

@app.route('/book', methods=['POST'])
def book():
    tour_id = request.form.get('tour_id')
    spots = int(request.form.get('spots'))

    tour = Tour.query.get(int(tour_id))
    if tour:
        if tour.spots >= spots:
            tour.spots -= spots
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return f"Not enough spots available for Tour {tour_id}"

    return "Tour not found"

@app.route('/tour/<int:tour_id>')
def tour_details(tour_id):
    tour = Tour.query.get(tour_id)
    if tour:
        return render_template('tour_details.html', tour=tour)
    return "Tour not found"

@app.route('/add_tour', methods=['GET', 'POST'])
def add_tour():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        duration = request.form['duration']
        price = float(request.form['price'])
        includes = request.form['includes']
        spots = int(request.form['spots'])

        new_tour = Tour(name=name, description=description, duration=duration, price=price, includes=includes, spots=spots)
        db.session.add(new_tour)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add_tour.html')

@app.route('/delete_tour/<int:tour_id>')
def delete_tour(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    db.session.delete(tour)
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        # Создаем базу данных и таблицу туров
        db.create_all()
    app.run(debug=True)
