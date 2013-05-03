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


def convert(moedict):
    the_dict = DictTAB()
    pool = Pool()
    for k, d in pool.map(generate_dict_entry, [
            e for e in moedict if not e['title'].startswith('{[')]):
        the_dict.add_article(k, d)
    return the_dict


def convert_from_json(fp):
    import json
    moedict = json.load(fp)
    the_dict = convert(moedict)
    print(repr(the_dict))


def get_definitions(conn, heteronyms_id):
    c = conn.cursor()
    rows = c.execute("select * from definitions where heteronym_id=?", (
        heteronyms_id,))
    results = []
    for row in rows:
        definition = dict(zip(['id', 'heteronym_id', 'idx', 'type', 'def', 'example', 'quote', 'synonyms', 'antonyms', 'link', 'source'],
            row))
        results.append(definition)
    return results


def get_heteronyms(conn, entry_id):
    c = conn.cursor()
    rows = c.execute("select * from heteronyms where entry_id=?", (
        entry_id,))
    results = []
    for row in rows:
        h = dict(zip(['id', 'entry_id', 'idx', 'bopomofo', 'bopomofo2', 'pinyin'],
            row))
        h['definitions'] = get_definitions(conn, row[1])
        results.append(h)
    return results


def get_entries(fn):
    import sqlite3
    conn = sqlite3.connect(fn)
    c = conn.cursor()

    results = []
    for row in c.execute(
            "select * from entries where title not like '{[%'"):
        entry = dict(zip(
            ['id', 'title', 'radical', 'stroke_count', 'non_radical_stroke_count', 'dict_id', 'heteronyms'], row))
        entry['heteronyms'] = get_heteronyms(conn, row[0])
        results.append(entry)

    return results


def convert_from_sqlite3(fn):
    import json
    entries = get_entries(fn)
    the_dict = convert(entries)
    print(repr(the_dict))


def main(args):
    if len(args) == 0:
        print('Need filename')
        sys.exit(-1)

    if args[0] == '-':
        print("Don't allow read from stdin.")
    else:
        # check whether file is existed.
        # convert_json(open(args[0]))
        convert_from_sqlite3(args[0])


if __name__ == "__main__":
    main(sys.argv[1:])
