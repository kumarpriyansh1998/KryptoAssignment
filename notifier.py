import requests
import sqlite3
import time
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from utils import execute_alter, execute_select, queries
logging.basicConfig(level=logging.INFO)
btc_api = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_d"


def send_email(mail_content, receiver_address, alert_data):
    sender_address = 'kryptokumar2021@gmail.com'
    sender_pass = 'Aezakmi@123'
    message = MIMEMultipart('alternative')
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = "Alert for BTC Price Update."

    part1 = MIMEText(mail_content, 'plain')
    message.attach(part1)

    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_address, sender_pass)  # login with mail_id and password
    text = message.as_string()
    logging.info("Sending Email now.")
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    execute_alter(queries['UPDATE'].format(**{'status': 'COMPLETED', 'id': alert_data['ID'],
                                              'user': alert_data['USER'], 'alert_price': alert_data['ALERT_PRICE']}))
    logging.info("Email Sent")


def process_alert(alert_data, btc_current_price):
    logging.info(
        f"Triggering Email. Details: \n Email: {alert_data['EMAIL']}, Alert Price: {alert_data['ALERT_PRICE']}, "
        f"Current Price: {btc_current_price}")
    execute_alter(queries['UPDATE'].format(**{'status': 'TRIGGERED', 'id': alert_data['ID'],
                                              'user': alert_data['USER'], 'alert_price': alert_data['ALERT_PRICE']}))
    message_body = f"""Hello {alert_data['USER']}, \n\n
    Your BTC Alert price set at {alert_data['ALERT_PRICE']} has reached current BTC price of {btc_current_price} . \n
    Please have a look as soon as possible. \n\n Thanks and Regards, \n Kumar Priyansh's BTC Notifier
    """
    send_email(message_body, alert_data['EMAIL'], alert_data)


while True:
    # Get alerts to execute
    try:
        logging.info(f"{'-'*50}")
        btc_data = requests.get(btc_api).json()[0]
        btc_price = btc_data['current_price']
        logging.info(f"Current BTC price: {btc_price}")
        # Get the records to Alert
        op = execute_select(queries['ALERT'].format(**{'btc_price': btc_price}))
        logging.info(f"ALERTS to TRIGGER: {[dict(x) for x in op]}")
        for x in op:
            _alert_data = dict(x)
            process_alert(_alert_data, btc_price)

    except Exception as e:
        logging.error(f"Error in Notifier: {e}")
    time.sleep(30)
