#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
try:
    from lxml import etree
except:
    print("Need lxml")
    sys.exit(-1)


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
        etree.SubElement(info, "date").text = "2013.4.25"  # TODO
        etree.SubElement(info, "dicttype").text = ""

    def add_article(self, key, definition):
        article_e = etree.SubElement(self.dic, "article")
        key_e = etree.SubElement(article_e, "key")
        key_e.text = key
        definition_e = etree.SubElement(article_e, "definition")
        definition_e.attrib['type'] = 'h'
        definition_e.text = etree.CDATA(definition)

    def __repr__(self):
        return etree.tostring(self.dic, pretty_print=True,
                xml_declaration=True)


class DictTAB:
    def __init__(self):
        self.lines = []

    def add_article(self, key, definition):
        try:
            self.lines.append("{0}\t{1}".format(
                key.encode('utf-8'), definition.encode('utf-8')))
        except UnicodeEncodeError, ex:
            print(ex)
            print(type(key))
            print(type(definition))

    def __repr__(self):
        return "\n".join(self.lines)
