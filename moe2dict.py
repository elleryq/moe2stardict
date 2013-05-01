#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Convert MOE dictionary data to stardict dict xml"""
import sys
import os
import json
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


def convert(fp):
    #the_dict = DictXML()
    the_dict = DictTAB()
    moedict = json.load(fp)
    pool = Pool()
    for k, d in pool.map(generate_dict_entry, [
            e for e in moedict if not e['title'].startswith('{[')]):
        the_dict.add_article(k, d)
    print(repr(the_dict))


def main(args):
    if len(args) == 0:
        print('Need filename')
        sys.exit(-1)

    if args[0] == '-':
        #convert(codecs.getreader('utf-8')(sys.stdin))
        convert(sys.stdin)
    else:
        # check whether file is existed.
        convert(open(args[0]))


if __name__ == "__main__":
    main(sys.argv[1:])
