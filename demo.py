from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BAZADANIX.db'
db = SQLAlchemy(app)

class BAZADANIX(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_number = db.Column(db.String(20), nullable=False) 
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    org_type = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Новая заявка')
    responsible = db.Column(db.String(100), nullable=True)
    date_completed = db.Column(db.DateTime)
    def __repr__(self):
        return f'<BAZADANIX {self.application_number}>'  
#POST запрос на обноволение и доавбление данных в бд
@app.route('/add', methods=['GET', 'POST'])
def add_application():  
    if request.method == 'POST':
        application_number = request.form['application_number']  
        org_type = request.form['org_type']
        model = request.form['model']
        description = request.form['description']
        client_name = request.form['client_name']
        phone_number = request.form['phone_number']

        new_application = BAZADANIX(  
            application_number=application_number,  
            org_type=org_type, 
            model=model,
            description=description,
            client_name=client_name,
            phone_number=phone_number
        )
        db.session.add(new_application)
        db.session.commit() 
        return redirect(url_for('index'))

    return render_template('add_application.html')  




# запрос на получение всех данных из бд
@app.route('/')
def index():
    applications = BAZADANIX.query.all()  
    return render_template('index.html', applications=applications)  
#запрос на редактирование данных
@app.route('/update/<int:application_id>', methods=['GET', 'POST']) 
def update_application(application_id):  
    application = BAZADANIX.query.get_or_404(application_id)  
    if request.method == 'POST':
        application.status = request.form['status']
        application.description = request.form['description']
        application.responsible = request.form['responsible']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update_application.html', application=application)  
# Пооиск по search_id
@app.route('/search', methods=['GET', 'POST'])
def search_application():
    if request.method == 'POST':
        search_id = request.form['search_id']
        application = BAZADANIX.query.filter_by(application_number=search_id).first()
        if application:
            return render_template('application_details.html', application=application)
        else:
            return "Заявка не найдена."
    return render_template('index.html')
#статистика "Количество выполненных заявок"
@app.route('/ad')
def statistics():
    completed_applications = BAZADANIX.query.filter_by(status='Завершена').count()

    # Среднее время выполнения заявки (в днях)
    total_time_in_days = 0
    completed_applications = BAZADANIX.query.filter_by(status='Завершена').all()
    for app in completed_applications:
        if app.date_completed and app.date_added:
            time_delta = app.date_completed - app.date_added  
            total_time_in_days += time_delta.days  
    average_time_in_days = total_time_in_days / len(completed_applications) if len(completed_applications) < 0 else 0
    completed_applications = BAZADANIX.query.filter_by(status='Завершена').count()

   
    return render_template('statistics.html', 
                           completed_applications=completed_applications,
                           average_time_in_days =average_time_in_days)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

