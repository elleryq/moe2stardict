#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Convert MOE dictionary data to stardict dict xml"""
import sys
from dictf import DictTAB
from multiprocessing import Pool
import argparse

ARG_SQLITE3 = 1
ARG_JSON = 2

import re
MORE_THAN_ONE_NEWLINE=re.compile(u'\n+')

try:
    from jinja2 import Environment
except:
    print("Need jinja2")
    sys.exit(-1)


HTML = """{{title}}
{% if radical %}{{ radical }} + {{ non_radical_stroke_count }} = {{ stroke_count }}{% endif %}
{% if heteronyms %}{% for h in heteronyms %}
    {% if h['bopomofo'] %}{{ h['bopomofo'] }}{% endif %}
    {% if h['definitions'] %}
      {% for d in h['definitions'] %}
        {{ d['def'] }}
        {% if h['quote'] %}
          {% for q in h['quote'] %}{{ q }}{% endfor %}
        {% endif %}
        {% if h['example'] %}
          {% for x in h['example'] %}{{ x }}{% endfor %}
        {% endif %}
        {% if h['link'] %}
          {% for l in h['link'] %}{{ l }}{% endfor %}
        {% endif %}
      {% endfor %}
    {% endif %}
  {% endfor %}{% endif %}
"""
TEMPLATE = Environment().from_string(HTML)


def remove_more_than_one_newline(s):
    return MORE_THAN_ONE_NEWLINE.sub(u'\n', s)


def generate_definition(entry):
    result = ""
    if 'title' in entry:
        content = TEMPLATE.render(entry).strip().replace(u' ', u'')
        result = remove_more_than_one_newline(content).replace(
            u'\n', u'\\n')
    return result


def generate_dict_entry(entry):
    definition = generate_definition(entry)
    return (entry['title'], definition)


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
        h['definitions'] = get_definitions(conn, row[0])
        results.append(h)
    return results


def get_entries(fn):
    import sqlite3
    conn = sqlite3.connect(fn)
    c = conn.cursor()

    results = []
    for row in c.execute(
            "select * from entries where title not like '%{[%'"):
        entry = dict(zip(
            ['id', 'title', 'radical', 'stroke_count', 'non_radical_stroke_count', 'dict_id', 'heteronyms'], row))
        entry['heteronyms'] = get_heteronyms(conn, row[0])
        results.append(entry)

    return results


def convert(moedict, parallel=True):
    the_dict = DictTAB()
    if parallel:
        pool = Pool()
        for k, d in pool.map(generate_dict_entry, moedict):
            the_dict.add_article(k, d)
    else:
        for k, d in map(generate_dict_entry, moedict):
            the_dict.add_article(k, d)
    return the_dict


def convert_from_json(fn, output_fd):
    import json
    moedict = json.load(open(fn, "rt"))
    the_dict = convert([entry for entry in moedict if '{[' not in entry['title']])
    output_fd.write(repr(the_dict))
    output_fd.write('\n')


def convert_from_sqlite3(fn, output_fd):
    entries = get_entries(fn)
    # real	0m15.853s
    # user	0m27.222s
    # sys	0m2.300s
    the_dict = convert(entries)
    # for profling.
    # real	0m15.367s
    # user	0m14.873s
    # sys	0m0.456s
    # the_dict = convert(entries, parallel=False)
    output_fd.write(repr(the_dict))
    output_fd.write('\n')


def main(args):
    if args.source_type == ARG_SQLITE3:
        convert_from_sqlite3(args.input_fn, args.output_fd)
    elif args.source_type == ARG_JSON:
        convert_from_json(args.input_fn, args.output_fd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("-i", "--input", dest="input_fn",
            help="source file", metavar="SOURCE_FILE",
            required=True)
    parser.add_argument("-t", "--type", dest="source_type",
            help="source file type (1:sqlite3, 2:json)", metavar="TYPE",
            type=int,
            choices=xrange(1, 3),
            default=ARG_SQLITE3)
    parser.add_argument("-o", "--output", dest="output_fd",
            help="write tabfile to FILE", metavar="FILE",
            type=argparse.FileType('wt'), required=True)
    args = parser.parse_args()

    main(args)
