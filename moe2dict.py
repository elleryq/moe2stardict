#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Convert MOE dictionary data to stardict dict xml"""
import sys
import os
from dictf import DictTAB
from multiprocessing import Pool

try:
    from jinja2 import Environment
except:
    print("Need jinja2")
    sys.exit(-1)


HTML = """{{title}}
{% if radical %}
  {{ radical }} + {{ non_radical_stroke_count }} = {{ stroke_count }}
{% endif %}
{% if heteronyms %}
  {% for h in heteronyms %}
    {% if h['bopomofo'] %}{{ h['bopomofo'] }}{% endif %}
    {% if h['definitions'] %}
      {% for d in h['definitions'] %}
        {{ d['def'] }}
        {% if h['quote'] %}
          {% for q in h['quote'] %}
            {{ q }}
          {% endfor %}
        {% endif %}
        {% if h['example'] %}
          {% for x in h['example'] %}
            {{ x }}
          {% endfor %}
        {% endif %}
        {% if h['link'] %}
          {% for l in h['link'] %}
            {{ l }}
          {% endfor %}
        {% endif %}
      {% endfor %}
    {% endif %}
  {% endfor %}
{% endif %}
"""


def generate_definition(entry):
    result = ""
    if 'title' in entry:
        result = Environment().from_string(HTML).render(
            entry).replace('\n', '\\n').replace(' ', '')
    return result


def generate_dict_entry(entry):
    definition = generate_definition(entry)
    return (entry['title'], definition)


def convert_from_json(fp):
    import json
    the_dict = DictTAB()
    moedict = json.load(fp)
    pool = Pool()
    for k, d in pool.map(generate_dict_entry, [
            e for e in moedict if not e['title'].startswith('{[')]):
        the_dict.add_article(k, d)
    print(repr(the_dict))


class Definitions:
    def __init__(self, row):
        self.row = row

    def __getattr__(self, name):
        if name == 'id':
            return self.row[0]
        elif name == 'idx':
            return self.row[2]
        elif name == 'type':
            return self.row[3].encode('utf-8')
        elif name == 'def':
            return self.row[4].encode('utf-8')
        elif name == 'example':
            return self.row[5].encode('utf-8')
        elif name == 'quote':
            return self.row[6].encode('utf-8')
        elif name == 'synonyms':
            return self.row[7].encode('utf-8')
        elif name == 'antonyms':
            return self.row[8].encode('utf-8')
        elif name == 'link':
            return self.row[9].encode('utf-8')
        elif name == 'source':
            return self.row[10].encode('utf-8')
        return None

    @staticmethod
    def get(conn, heteronyms_id):
        c = conn.cursor()
        rows = c.execute("select * from definitions where heteronym_id=?", (
            heteronyms_id,))
        results = []
        for row in rows:
            results.append(Definitions(row))
        return results


class Heteronyms:
    def __init__(self, conn, row):
        self.conn = conn
        self.row = row

    def __getattr__(self, name):
        if name == 'id':
            return self.row[0]
        elif name == 'idx':
            return self.row[2]
        elif name == 'bopomofo':
            return self.row[3].encode('utf-8')
        elif name == 'bopomofo2':
            return self.row[4].encode('utf-8')
        elif name == 'pinyin':
            return self.row[5].encode('utf-8')
        elif name == 'definitions':
            return Definitions.get(self.conn, self.row[1])
        return None

    @staticmethod
    def get(conn, entry_id):
        c = conn.cursor()
        rows = c.execute("select * from heteronyms where entry_id=?", (
            entry_id,))
        results = []
        for row in rows:
            results.append(Heteronyms(conn, row))
        return results


class Entry(object):
    def __init__(self, conn, row):
        self.conn = conn
        self.row = row
        self.id = row[0]
        self.title = row[1]
        self.radical = row[2]
        self.stroke_count = row[3]
        self.non_radical_stroke_count = row[4]
        self.dict_id = row[5]
        self.heteronyms = Heteronyms.get(conn, self.id)

    @staticmethod
    def all(fn):
        import sqlite3
        conn = sqlite3.connect(fn)
        c = conn.cursor()

        results = []
        for entry in c.execute(
                "select * from entries where title not like '{[%'"):
            results.append(Entry(conn, entry))

        return results


def convert_from_sqlite3(fn):
    import json
    entries = Entry.all(fn)
    print(len(entries))
    print(entries[0:10])
    #for entry in entries:
    #    print(repr(entry))
    #print(json.dumps(entries))
    print("Need implement")


def main(args):
    if len(args) == 0:
        print('Need filename')
        sys.exit(-1)

    if args[0] == '-':
        #convert(sys.stdin)
        print("Don't allow read from stdin.")
    else:
        # check whether file is existed.
        # convert(open(args[0]))
        convert_from_sqlite3(args[0])


if __name__ == "__main__":
    main(sys.argv[1:])
