#!flask/bin/python
from flask import Flask, abort, request, json, Response
from time import time
from uuid import uuid1
import json
import sqlite3


db_file = 'notes.db'
conn = sqlite3.connect(db_file)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS notes
             (id text, title text, text text, date_create int, date_update int);''')
conn.commit()
conn.close()

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello!"


@app.errorhandler(404)
def not_found(error):
    return Response(json.dumps({'error': 'Not found'}), status=404, mimetype='application/json')


@app.route('/notes', methods=['GET'])
def get_notes():
    with sqlite3.connect(db_file) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM notes;')
        all_rows = c.fetchall()
        notes = [{'id':row[0], 'title':row[1], 'text':row[2], 'date_create':row[3], 'date_update':row[4]} for row in all_rows]
        conn.commit()
        return Response(json.dumps(notes), status=200, mimetype='application/json')


@app.route('/notes/<string:note_id>', methods=['GET'])
def get_note(note_id):
    with sqlite3.connect(db_file) as con:
        c = con.cursor()
        c.execute('SELECT * FROM notes where id="{}";'.format(note_id))
        row = c.fetchall()
        if not row:
            abort(404)
        note = {'id': row[0][0], 'title': row[0][1], 'text': row[0][2], 'date_create': row[0][3], 'date_update': row[0][4]}
        con.commit()
        return Response(json.dumps(note), status=200, mimetype='application/json')


@app.route('/notes', methods=['POST'])
def create_note():
    title_text = json.loads(request.get_data())
    with sqlite3.connect(db_file) as con:
        c = con.cursor()
        c.execute("INSERT INTO notes VALUES ('{}','{}','{}','{}','{}')".format(str(uuid1()),
                    title_text['title'], title_text['text'], int(time()), int(time())))
        con.commit()
        return Response(status=201)


@app.route('/notes/<string:note_id>', methods=['PUT'])
def put_note(note_id):
    title_text = json.loads(request.get_data())
    with sqlite3.connect(db_file) as con:
        c = con.cursor()
        c.execute('SELECT * FROM notes where id="{}";'.format(note_id))
        row = c.fetchall()
        if not row:
            abort(404)
        c.execute('UPDATE notes SET title="{}",text="{}",date_update="{}" WHERE id="{}";'.format(title_text['title'], title_text['text'], int(time()), note_id))
        c.execute('SELECT * FROM notes WHERE id="{}";'.format(note_id))
        row = c.fetchall()
        note = {'id': row[0][0], 'title': row[0][1], 'text': row[0][2], 'date_create': row[0][3], 'date_update': row[0][4]}
        con.commit()
        return Response(json.dumps(note), status=200, mimetype='application/json')


@app.route('/notes/<string:note_id>', methods=['DELETE'])
def delete_note(note_id):
    with sqlite3.connect(db_file) as con:
        c = con.cursor()
        c.execute('SELECT * FROM notes WHERE id="{}";'.format(note_id))
        if not c.fetchall():
            abort(404)
        c.execute('DELETE FROM notes WHERE id="{}";'.format(note_id))
        con.commit()
        return Response(status=200)


if __name__ == '__main__':
    app.run(port=8080, debug=True)
