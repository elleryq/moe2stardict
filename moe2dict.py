#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Convert MOE dictionary data to stardict dict xml"""
import sys
import os
import codecs
import json
try:
    from jinja2 import Environment
except:
    print("Need jinja2")
    sys.exit(-1)

try:
    from lxml import etree
except:
    print("Need lxml")
    sys.exit(-1)


HTML = """
<h1>{{title}}</h1>
{% if radical %}
<p> {{ radical }} + {{ non_radical_stroke_count }} = {{ stroke_count }} </p>
{% endif %}
{% if heteronyms %}
    {% for h in heteronyms %}
        <div>
            {% if h['bopomofo'] %}
                <p>{{ h['bopomofo'] }}</p>
            {% endif %}
            {% if h['definitions'] %}
              <ol>
              {% for d in h['definitions'] %}
                <li><p>
                    <span>{{ d['def'] }}</span>
                    {% if h['quote'] %}
                      <span>
                      {% for q in h['quote'] %}
                        {{ q }}
                      {% endfor %}
                      </span>
                    {% endif %}
                    {% if h['example'] %}
                      <span>
                      {% for x in h['example'] %}
                        {{ x }}
                      {% endfor %}
                      </span>
                    {% endif %}
                    {% if h['link'] %}
                      <span>
                      {% for l in h['link'] %}
                        {{ l }}
                      {% endfor %}
                      </span>
                    {% endif %}
                </p></li>
              {% endfor %}
              </ol>
            {% endif %}
        </div>
    {% endfor %}
{% endif %}
"""

def generate_html(entry):
    result = ""
    if 'title' in entry:
        result = Environment().from_string(HTML).render(entry)
    return result


class DictXML:
    def __init__(self):
        self.dic = etree.Element("stardict")
        info = etree.SubElement(self.dic, "info")
        etree.SubElement(info, "version").text = "2.4.2"
        etree.SubElement(info, "bookname").text = "moedict"
        etree.SubElement(info, "author").text = ""
        etree.SubElement(info, "email").text = ""
        etree.SubElement(info, "website").text = ""
        etree.SubElement(info, "description").text = ""
        etree.SubElement(info, "date").text = "2013.4.25" #TODO
        etree.SubElement(info, "dicttype").text = ""

    def add_article(self, key, definition):
        article_e = etree.SubElement(self.dic, "article")
        key_e = etree.SubElement(article_e, "key")
        key_e.text = key
        definition_e = etree.SubElement(article_e, "definition")
        definition_e.attrib['type']='h'
        definition_e.text = etree.CDATA(definition)

    def __repr__(self):
        return etree.tostring(self.dic, 
                pretty_print=True,
                xml_declaration=True)


def convert(fp):
    xml = DictXML()
    moedict = json.load(fp)
    for entry in moedict[:100]:
        html = generate_html(entry)
        xml.add_article(entry['title'], html)
    print(repr(xml))


def main(args):
    if len(args)==0:
        print('Need filename')
        sys.exit(-1)

    if args[0]=='-':
        #convert(codecs.getreader('utf-8')(sys.stdin))
        convert(sys.stdin)
    else:
        # check whether file is existed.
        convert(open(args[0]))


if __name__ == "__main__":
    main(sys.argv[1:])

