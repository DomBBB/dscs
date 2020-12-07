# Download the twilio-python library from twilio.com/docs/libraries/python
from twilio.rest import Client
import psycopg2
import requests
import os
import datetime
from passwords1 import psql_user, psql_pw, psql_host, psql_port, psql_database, email_auth, email_data, sms_account_sid, sms_auth_token, sms_data


def send_email(matched_email_list):
    script_dir = os.path.dirname(__file__)
    rel_path = "Email/"
    name = "alert.html"
    file_path = os.path.join(script_dir, rel_path, name)
    r = open(file_path,"r")
    html_file = r.read()
    mess = _send_email(email_auth, matched_email_list, html_file, email_data)
    print(mess)
    return


def _send_email(key, bcc, html_file, email_data):
    result = requests.post("https://api.eu.mailgun.net/v3/mail.schuldenrufe.ch/messages",
                           auth=("api", key),
                           data={"from": email_data[0], "to": email_data[1],"bcc": bcc, "subject": "Alert triggered!", "html": html_file})
    return result


def send_sms(matched_sms_list):
    body = "Your schuldenrufe.ch Alert was triggered. Please check your Cockpit for further information."
    for number in matched_sms_list:
        x = _send_sms(sms_account_sid, sms_auth_token, number, body, sms_data)
        if x == True:
            print("sms sent to: " + number)
        else:
            print("not sent: " + number)
    return


def _send_sms(account_sid, auth_token, phone_number, sms_body, sms_data):
    client = Client(account_sid, auth_token)
    try:
        client.api.account.messages.create(
            to=phone_number,
            from_=sms_data,
            body=sms_body)
        return True
    except:
        return False


def check_for_matches():
    """ Creates unique lists for sms and email for entries that are both in search_words and liquidations if they were entered at the date this function is executed. """
    matches=[]
    current_dt = datetime.datetime.now()
    matched = query("SELECT username FROM search_words WHERE EXISTS (SELECT che FROM liquidations WHERE liquidations.che=search_words.che AND insertdate= current_date)")
    for match in matched:
        matches.append(match[0])
    match_ls = list(set(matches))
    contacts = []
    for m in match_ls:
        res = query("SELECT phone, email FROM contacts WHERE username='{}'".format(m))
        contacts.append(res)

    phone_ls = []
    email_ls = []
    for c in contacts:
        for c_details in c:
            if c_details[0] != '':
                phone_ls.append(c_details[0])
            if c_details[1] != '':
                email_ls.append(c_details[1])
    matched_sms_list = list(set(phone_ls))
    email_ls = list(set(email_ls))
    matched_email_list = []
    for x in email_ls:
        matched_email_list.append([x])
    print(matched_sms_list)
    print(matched_email_list)
    return matched_sms_list, matched_email_list


def get_psql_connection():
    return psycopg2.connect(
            user = psql_user,
            password = psql_pw,
            host = psql_host,
            port = psql_port,
            database = psql_database
    )


def query(cmd):
    return _query(cmd, True)


def query_no_fetch(cmd):
    _query(cmd, False)


def _query(cmd, fetch):
    connection = get_psql_connection()
    cursor = connection.cursor()
    cursor.execute(cmd)
    connection.commit()
    if(fetch):
        res = cursor.fetchall()
        cursor.close()
        connection.close()
        return res
    cursor.close()
    connection.close()
    return


matched_sms_list, matched_email_list = check_for_matches()
send_email(matched_email_list)
send_sms(matched_sms_list)
