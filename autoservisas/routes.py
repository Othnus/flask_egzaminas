from flask import redirect, request, render_template, flash, url_for
from flask_bcrypt import Bcrypt
from flask_login import logout_user, login_user, login_required, current_user

from autoservisas.models import User, Car, Failure, LimitedAdmin
from autoservisas import forms
from autoservisas import app, db, admin


admin.add_view(LimitedAdmin(User, db.session))
admin.add_view(LimitedAdmin(Car, db.session))
admin.add_view(LimitedAdmin(Failure, db.session))
bcrypt = Bcrypt(app)


@app.route("/admin")
@login_required
def admin():
    return redirect(url_for(admin))


@app.route('/')
def home():
    flash('Sveiki atvykę į geriausią autoservisą!', 'info')
    return render_template('base.html', current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next')
    if current_user.is_authenticated:
        flash('Vartotojas jau prisijungęs. Atsijunkite, norint prisijungti kitu vartotoju')
        return redirect(next_page) if next_page else redirect(url_for('home'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(e_mail=form.e_mail.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Sėkmingai prisijungėte. Sveiki atvykę, {current_user.login}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('!Prisijungti nepavyko!', 'danger')
    return render_template('login.html', form=form, current_user=current_user)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        flash('Išsiregistruokite, kad sukurti nauja vartotoją')
        return redirect(url_for('home'))
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        hidden_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        is_first_user = not User.query.first()
        new_user = User(
            login=form.login.data,
            e_mail=form.e_mail.data,
            password=hidden_password,
            is_admin=is_first_user,
            is_worker=is_first_user
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Sėkmingai prisiregistravote! Galite prisijungti.', 'success')
        except:
            flash('Toks vartotojas arba el. paštas jau egzistuoja sistemoje', 'danger')
        return redirect(url_for('home'))
    return render_template('registration.html', form=form, current_user=current_user)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = forms.ProfileForm()
    if form.validate_on_submit():
        try:
            current_user.login = form.login.data
            current_user.e_mail = form.e_mail.data
            db.session.commit()
            flash('Profilis atnaujintas!', 'success')
        except:
            flash('Toks vartotojas arba el. paštas jau egzistuoja sistemoje!', 'danger')
        return redirect(url_for('profile'))
    elif request.method == "GET":
        form.login.data = current_user.login
        form.e_mail.data = current_user.e_mail
    return render_template('profile.html', current_user=current_user, form=form)


@app.route('/cars', methods=['GET', 'POST'])
@login_required
def cars():
    try:
        all_my_cars = Car.query.filter_by(user_id=current_user.id).all()
    except:
        all_my_cars = []
    return render_template("cars.html", all_my_cars=all_my_cars)


@app.route("/new_car", methods=["GET", "POST"])
def new_car():
    form = forms.CarForm()
    if form.validate_on_submit():
        new_car = Car(
            marke=form.marke.data,
            model=form.model.data,
            year=form.year.data,
            engine=form.engine.data,
            registration=form.registration.data,
            vin=form.vin.data,
            user_id=current_user.id
        )
        try:
            db.session.add(new_car)
            db.session.commit()
            flash(f'Automobilis {new_car} sekmingai sukurtas', 'success')
        except:
            flash('Automobilis su tokiu valstybiniu numeriu arba VIN jau egzistuoja sistemoje', 'danger')
        return redirect(url_for('cars'))
    return render_template("car_form.html", form=form)


@app.route("/edit_car/<int:id>", methods=["GET", "POST"])
def edit_car(id):
    form = forms.CarForm()
    try:
        car = Car.query.get(id)
    except:
        return redirect(url_for('cars'))
    if form.validate_on_submit():
        car.marke = form.marke.data
        car.model = form.model.data
        car.year = form.year.data
        car.engine = form.engine.data
        car.registration = form.registration.data
        car.vin = form.vin.data
        try:
            db.session.commit()
            flash(f'Automobilis {car} sėkmingai atnaujintas', 'success')
        except:
            flash('Automobilis su tokiu valstybiniu numeriu arba VIN jau egzistuoja sistemoje', 'danger')
        return redirect(url_for('cars'))
    return render_template("car_form.html", form=form, car=car)


@app.route("/delete_car/<int:id>")
def delete_car(id):
    try:
        car = Car.query.get(id)
    except:
        return redirect(url_for('cars'))
    db.session.delete(car)
    db.session.commit()
    flash(f'Automobilis {car} sėkmingai pašalintas', 'danger')
    return redirect(url_for('cars'))


@app.route('/failures', methods=['GET', 'POST'])
@login_required
def failures():
    try:
        all_failures = Failure.query.all()
    except:
        all_failures = []
    return render_template("failures.html", all_failures=all_failures)


@app.route('/car_failuress/<int:id>', methods=['GET', 'POST'])
@login_required
def car_failures(id):
    try:
        car = Car.query.get(id)
    except:
        return redirect(url_for('cars'))
    try:
        all_car_failures = Failure.query.filter_by(car_id=car.id).all()
    except:
        all_car_failures = []
    return render_template("car_failures.html", all_car_failures=all_car_failures, car=car)


@app.route("/new_failure", methods=["GET", "POST"])
@login_required
def new_failure():
    form = forms.CreateFailureForm()
    if form.validate_on_submit():
        new_failure = Failure(description=form.description.data)
        if hasattr(form.car_id.data, 'id'):
            new_failure.car_id = form.car_id.data.id
        db.session.add(new_failure)
        db.session.commit()
        flash(f'Automobilio gedimas sėkmingai užregistruotas', 'success')
        return redirect(url_for('cars'))
    return render_template("create_failure_form.html", form=form, car=False)


@app.route("/edit_failure/<int:id>", methods=["GET", "POST"])
@login_required
def edit_failure(id):
    form = forms.EditFailureForm()
    try:
        failure = Failure.query.get(id)
        car = Car.query.get(id)
    except:
        return redirect(url_for('failures'))
    if form.validate_on_submit():
        failure.status = form.status.data
        failure.price = form.price.data
        db.session.commit()
        flash(f'Automobilio gedimas sekmingai atnaujintas', 'success')
        return redirect(url_for('failures'))
    return render_template("edit_failure_form.html", form=form, failure=failure, car=car)


@app.route("/delete_failure/<int:id>")
def delete_failure(id):
    try:
        failure = Failure.query.get(id)
    except:
        return redirect(url_for('failures'))
    db.session.delete(failure)
    db.session.commit()
    flash(f'Automobilio gedimas sėkmingai ištrintas', 'danger')
    return redirect(url_for('failures'))


@app.route('/logout')
def logout():
    logout_user()
    next_page = request.args.get('next')
    return redirect(next_page) if next_page else redirect(url_for('home'))
