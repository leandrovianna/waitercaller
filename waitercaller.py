import datetime
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import LoginManager
from flask_login import login_user
from flask_login import login_required
from flask_login import logout_user
from bitlyhelper import BitlyHelper
import config
from forms import CreateTableForm
from forms import LoginForm
from forms import RegistrationForm
from mockdbhelper import MockDBHelper as DBHelper
from passwordhelper import PasswordHelper
from user import User

app = Flask(__name__)
app.secret_key = 'DiEiKHlsXlriJxEFk+85YoT64QxIaz6BMCnnVTjJClI9jGEQdQE3Rgf96jNO'
login_manager = LoginManager(app)
db = DBHelper()
ph = PasswordHelper()
bh = BitlyHelper()


@app.route('/')
def home():
    return render_template('home.html',
                           registrationform=RegistrationForm(),
                           loginform=LoginForm())


@app.route('/dashboard')
@login_required
def dashboard():
    now = datetime.datetime.now()
    requests = db.get_requests(current_user.get_id())
    for req in requests:
        deltaseconds = (now - req['time']).seconds
        req['wait_minutes'] = '{}.{}'.format(deltaseconds // 60,
                                             str(deltaseconds % 60).zfill(2))

    return render_template('dashboard.html', requests=requests)


@app.route('/dashboard/resolve')
@login_required
def dashboard_resolve():
    request_id = request.args.get('request_id')
    db.delete_request(request_id)
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['POST'])
def login():
    form = LoginForm(request.form)
    if form.validate():
        stored_user = db.get_user(form.loginemail.data)
        if stored_user and \
                ph.validate_password(form.loginpassword.data,
                                     stored_user['salt'], stored_user['hashed']):
            user = User(form.loginemail.data)
            login_user(user, remember=True)
            return redirect(url_for('account'))
        form.loginemail.errors.append('Email or password invalid')
    return render_template('home.html', loginform=form,
                           registrationform=RegistrationForm())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['POST'])
def register():
    form = RegistrationForm(request.form)
    if form.validate():
        if db.get_user(form.email.data):
            form.email.errors.append('Email address already registered')
            return render_template('home.html',
                                   registrationform=form,
                                   loginform=LoginForm())

        salt = ph.get_salt()
        hashed = ph.get_hash(form.password.data + salt)
        db.add_user(form.email.data, salt, hashed)
        return render_template('home.html', registrationform=form,
                               onloadmessage='Registration successful. Please log in.',
                               loginform=LoginForm())

    return render_template('home.html', registrationform=form,
                           loginform=LoginForm())


@login_manager.user_loader
def load_user(user_id):
    user_password = db.get_user(user_id)
    if user_password:
        return User(user_id)


@app.route('/account')
@login_required
def account():
    return render_template('account.html',
                           createtableform=CreateTableForm(),
                           tables=db.get_tables(current_user.get_id()))


@app.route('/account/createtable', methods=['POST'])
@login_required
def account_createtable():
    form = CreateTableForm(request.form)
    if form.validate():
        tableid = db.add_table(form.tablenumber.data, current_user.get_id())
        new_url = bh.shorten_url(config.base_url + 'newrequest/' + tableid)
        db.update_table(tableid, new_url)
        return redirect(url_for('account'))

    return render_template('account.html', createtableform=form,
                           tables=db.get_tables(current_user.get_id()))


@app.route('/account/deletetable')
@login_required
def account_deletetable():
    tableid = request.args.get('tableid')
    db.delete_table(tableid)
    return redirect(url_for('account'))


@app.route('/newrequest/<tid>')
def new_request(tid):
    db.add_request(tid, datetime.datetime.now())
    return 'Your request has been logged and a waiter will \
            be with you shortly'


if __name__ == "__main__":
    app.run(port=5000, debug=True)
