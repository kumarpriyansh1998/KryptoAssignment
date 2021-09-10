from utils import queries, execute_alter, execute_select, create_table
from flask import Flask, request, jsonify, session
from functools import wraps
import logging
import datetime
import jwt

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'This is for Krypto'


def check_token(func):
    @wraps(func)
    def inner_func(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message:': 'Missing Token'})
        try:
            _ = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        except Exception as e:
            return jsonify({'message': 'Token is invalid'})
        return func(*args, **kwargs)
    return inner_func


@app.route('/alerts/check')
def home():
    return {'Message': 'Services are up and Running. Good to go..'}


@app.route('/alerts/token', methods=['POST'])
def get_jwt():
    try:
        session['logged_in'] = True
        token = jwt.encode({
                    'user': request.form['user'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=600)  # Token Is Valid for 10 Mins
                    }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    except Exception as e:
        return jsonify({'error': f'Unable to fetch jwt token. {e}'})


@app.route('/alerts/create', methods=['POST'])
@check_token
def create():
    if request.method == 'POST':
        logging.info("Received Create request.")
        try:
            user_req = request.form
            user = user_req['user']
            email = user_req['email']
            alert_price = user_req['alert_price']
            execute_alter(queries['INSERT'].format(**{'user': user, 'email': email, 'alert_price': alert_price}))
            return jsonify({'message': 'Alert Created.'})
        except Exception as e:
            logging.exception(f"Error occurred in create API: {e}")
            return jsonify({'error': f'{str(e)}'})


@app.route('/alerts/delete', methods=['POST'])
@check_token
def delete():
    if request.method == 'POST':
        logging.info("Received delete Request")
        try:
            user_req = request.form
            user = user_req['user']
            alert_price = user_req['alert_price']
            execute_alter(queries['DELETE'].format(**{'user': user, 'alert_price': alert_price}))
            return jsonify({'message': 'Alert Deleted.'})
        except Exception as e:
            logging.exception(f"Error occurred in delete API: {e}")
            return jsonify({'error': f'{str(e)}'})

@app.route('/alerts/fetch', methods=['POST'])
@check_token
def fetch():
    if request.method == 'POST':
        logging.info("Received Fetch Request")
        try:
            user_req = request.form
            user = user_req['user']
            user_alerts = execute_select(queries['FETCH'].format(**{'user': user}))
            return jsonify({'message': [dict(x) for x in user_alerts]})

            return
        except Exception as e:
            logging.exception(f"Error occurred in fetch API: {e}")
            return jsonify({'error': f'{str(e)}'})


if __name__ == '__main__':
    create_table()
    app.run(debug=True, port=5005)
