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
"""

def generate_html(entry):
    result = ""
    if 'title' in entry:
        #print(entry['title'])
        result = Environment().from_string(HTML).render( {
            'title': entry['title'],
            })
    return result


class DictXML:
    def __init__(self):
        self.dic = etree.Element("stardict")
        self.dic.append(etree.Element("info"))

    def add_article(self, key, definition):
        article_e = etree.SubElement(self.dic, "article")
        key_e = etree.SubElement(article_e, "key")
        key_e.text = key
        definition_e = etree.SubElement(article_e, "definition")
        definition_e.text = etree.CDATA(definition)

    def __repr__(self):
        return etree.tostring(self.dic, 
                pretty_print=True,
                xml_declaration=True)


def convert(fp):
    xml = DictXML()
    moedict = json.load(fp)
    for entry in moedict:
        html = generate_html(entry)
        xml.add_article('1', html)
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

