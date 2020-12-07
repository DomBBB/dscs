from PyPDF2 import PdfFileReader
import requests
import os
import psycopg2
import datetime
from passwords1 import psql_user, psql_pw, psql_host, psql_port, psql_database


def  liq_all_cantons():
    """ Opens the current SHAB pdf and splits the content into entries for each Liquidationsschuldenruf. Then calls save_to_db with these entries. """
    pdf_path = "aktuelle_ausgabe.pdf"

    r = requests.get("https://www.shab.ch/api/v1/archive/issue-of-today?tenant=shab&language=de")
    with open(pdf_path, "wb") as f:
        f.write(r.content)

    pdf = PdfFileReader(pdf_path)
    page_content = ""
    i = 1
    while i < pdf.getNumPages():
        page_content = page_content + pdf.getPage(i).extractText()
        i += 1
    try:
        page_splitted = page_content[page_content.index("Liquidationsschuldenrufe"):page_content.index("Weitere gesellschaftsrechtliche Schuldenrufe")]
    except:
        page_splitted = page_content[page_content.index("Liquidationsschuldenrufe"):page_content.index("Schuldbetreibungen")]
    page_splitted = page_splitted[1:]
    content_list = []
    while True:
        try:
            x, y = split_content(page_splitted)
            content_list.append("L"+x)
            page_splitted = y[1:]
        except:
            try:
                x = page_splitted
                content_list.append("L"+x)
                break
            except:
                break

    os.remove(pdf_path)
    save_to_db(content_list)


def split_content(page_splitted):
    """ Helper function for the function liq_all_cantons() to split before and after the term Liquidationsschuldenruf. """
    content_splitted = page_splitted[:page_splitted.index("Liquidationsschuldenruf")]
    page_splitted = page_splitted[page_splitted.index("Liquidationsschuldenruf"):]
    return content_splitted, page_splitted


def save_to_db(x):
    """ Uses the entries from liq_all_cantons() to create all values and insert them in the psql table. """
    if(len(x) == 0):
        print("save_to_db:: received list was empty")
        return

    i = 0

    VALUES = None

    j = 0
    print(len(x))

    while VALUES == None and i < len(x):
        print(j)
        j+= 1
        VALUES = create_values_command(x[i])
        i += 1

    if(i == len(x)):
        print("save_to_db:: no elements found with non null names")
        return


    for k in x[i:]:
        print(str(j)+"*")
        j+= 1
        value = create_values_command(k)

        if value != None:
            VALUES += ",  " + value

    query_no_fetch("INSERT INTO liquidations VALUES {} ON CONFLICT (name) DO UPDATE SET type=EXCLUDED.type, name=EXCLUDED.name, che=EXCLUDED.che, date=EXCLUDED.date, contact=EXCLUDED.contact, insertdate=EXCLUDED.insertdate;".format(VALUES))


def create_values_command(i):
    """ Helper function for save_to_db to search for the defined values in the entries from liq_allcantons. """
    a,b,c,d,e = None, None, None, None, None
    try:
        a = i[i.index("Veröffentlichung") -3 : i.index("Veröffentlichung") + 16]
    except:
        pass

    try:
        b = i[i.index("Liquidationsschuldenruf") + 24 : i.index("Aufgelöstes Unternehmen") - 21]
    except:
        return None

    try:
        c = i[i.index("CHE-") : i.index("CHE-") + 15]
    except:
        pass
    if c == None:
        try:
            r = requests.post("https://www.zefix.ch/ZefixREST/api/v1/firm/search.json", json={"name":b ,"languageKey":"de", "maxEntries":1})
            x = r.json()["list"][0]["uid"]
            c = x[0:3] + "-" + x[3:6] + "." + x[6:9] + "." + x[9:12]
        except Exception as e:
            print(str(e))
            pass

    try:
        d = datetime.datetime.strptime(i[i.index("Ablauf der Frist") + 18: i.index("Ablauf der Frist") + 28], "%d.%m.%Y")
    except Exception as e:
        print(str(e))
        pass

    try:
        e = i[i.index("Kontaktstelle") + 15 : ]
    except:
        pass
    try:
        e = e[ : e.index("Bemerkungen") - 1]
    except:
        pass
    try:
        e = e[ : e.index("Hinweise zur Rechtsgültigkeit") - 1]
    except:
        pass

    if d == None:
        if a == "3. Veröffentlichung":
            date = datetime.datetime.now() + datetime.timedelta(30)
            return "({}, {}, {}, '{}', {}, '{}')".format(make_safe(a), make_safe(b), make_safe(c), date.strftime('%Y-%m-%d'), make_safe(e), datetime.datetime.now().strftime('%Y-%m-%d'))
        return "({}, {}, {}, null, {}, '{}')".format(make_safe(a), make_safe(b), make_safe(c), make_safe(e), datetime.datetime.now().strftime('%Y-%m-%d'))
    else:
        return "({}, {}, {}, '{}', {}, '{}')".format(make_safe(a), make_safe(b), make_safe(c), d.strftime('%Y-%m-%d'), make_safe(e), datetime.datetime.now().strftime('%Y-%m-%d'))


def make_safe(s):
    """ Helper function to create safe psql strings."""
    if s == None:
        return "null"

    return "'" + s.replace("'", "''") + "'"


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


def delete_liquidations():
    """ Delete all entries in liquidations 7 days after the deadline. """
    query_no_fetch("DELETE FROM liquidations WHERE date < current_date - interval '30 days'")


liq_all_cantons()
delete_liquidations()
