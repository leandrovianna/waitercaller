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
    return render_template('home.html')


@app.route('/account')
@login_required
def account():
    tables = db.get_tables(current_user.get_id())
    return render_template('account.html', tables=tables)


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
    email = request.form.get('email')
    password = request.form.get('password')
    stored_user = db.get_user(email)
    print(stored_user)
    if stored_user and ph.validate_password(password, stored_user['salt'], stored_user['hashed']):
        user = User(email)
        login_user(user, remember=True)
        return redirect(url_for('account'))
    return home()


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    pw1 = request.form.get('password')
    pw2 = request.form.get('password2')
    if not pw1 == pw2:
        return redirect(url_for('home'))
    if db.get_user(email):
        return redirect(url_for('home'))
    salt = ph.get_salt()
    hashed = ph.get_hash(pw1 + salt)
    db.add_user(email, salt, hashed)
    return redirect(url_for('home'))


@login_manager.user_loader
def load_user(user_id):
    user_password = db.get_user(user_id)
    if user_password:
        return User(user_id)


@app.route('/account/createtable', methods=['POST'])
@login_required
def account_createtable():
    tablename = request.form.get('tablenumber')
    tableid = db.add_table(tablename, current_user.get_id())
    new_url = bh.shorten_url(config.base_url + 'newrequest/' + tableid)
    db.update_table(tableid, new_url)
    return redirect(url_for('account'))


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
