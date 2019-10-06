#!/opt/local/bin/python
# -*- encoding: utf-8 -*-
# $Lastupdate: Sat Jun 10 12:11:45 2017 $
# $Createdate: Fri May 10 16:56:03 2013 $
#
# a collection of functions for analyzing BNC-XML
#
#
# common variables
#    BNC_ROOT
#    BNCdoc_pattern
#    BNCdoc_pattern2
#
#    list_W
#    list_SD
#    list_SC
#
# functions
#    abs_path(file_id)
#    BNCdoc_IDs()      : generates BNCdoc_ID's from current directory
#    parse_title(BNCdoc_ID)
#    containers(s_node) : returns a string showing its document position
# 

import re
import os
import sys
from lxml import etree as et

# import codecs
# sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)

HOME = os.getenv("HOME")
BNC_ROOT = HOME + '/data/corpus/BNC-XML/texts'
BNCdoc_pattern = re.compile(r"^(([A-K]).).\.xml")
BNCdoc_pattern2 = re.compile(r"^(([A-K]).).")     # without .xml extention

file_list = open('bnc_W_SD_SC.txt', 'r')
list_W = []
list_SD = []
list_SC = []
for line in file_list:
    (id, WSDSC) = line.split()
    if WSDSC == "W":
        list_W.append(id)
    elif WSDSC == "SC":
        list_SC.append(id)
    elif WSDSC == "SD":
        list_SD.append(id)
    else:
        print('error')



def abs_path(file_id):
    """
    for a given BNCdoc file id, e.g. AB2, KH1, ...,
    return its absolute path specification
    """
    id1, id2 = re.match(BNCdoc_pattern2, file_id).groups()
    return BNC_ROOT + "/" + id2 + "/" + id1 + "/" + file_id + ".xml"


def BNCdoc_IDs():
    """
    generator function that enumerates all the BNCdocs under
    the BNC_ROOT node
    """
    for path, subdirs, files in os.walk(BNC_ROOT):
        for file in files:
            if re.match(BNCdoc_pattern, file):
                yield file[:-4]
                

def parse_title(tree):
    title_W = re.compile(r"""^\s*(.*)\s+
              Sample\s+containing\s+about\s+(\d+)\s+words\s+
              (.*)\s+\(domain:\s+(.*)\)\s*$""", re.X)

    title_SC = re.compile(r"""^\s*(.*)\s+
              Sample\s+containing\s+about\s+(\d+)\s+words\s+
              (speech\s+recorded\s+in\s+(.*)\s+context)\s*$""", re.X)

    title_SD = re.compile(r"""^\s*(\d+)\s+conversations?\s+
              recorded\s+by\s+(.+)\s+ 
              (((between|on)\b.*)|(\[dates?\s+unknown\]))\s+
              with\s+(\d+)\s+interlocutors?,\s+ 
              totalling\s+(\d+)\s+s-units,\s+
              (\d+)\s+words(,\s+and)?\s+
              (.+)\.\s*$""", re.X)

    title_SD2 = re.compile(r"""^\s*((\d+)\s+conversations?)\s+
              recorded\s+by\s+`(\w+)'\s+\((PS...)\)\s+ 
              (.*)\s+
              with\s+(\d+)\s+interlocutors?,\s+ 
              totalling\s+(\d+)\s+s-units,\s+
              (\d+)\s+words(,\s+and)?\s+
              (.+)\.\s*$""", re.X)

    id = tree.xpath('//idno[@type="bnc"]')[0].text
    title = tree.xpath('//fileDesc/titleStmt/title')[0].text
            
    if title_W.match(title):
        m = title_W.match(title)
        category = 'W'                         # Written
        (short_title, words, medium, genre) = m.groups()
        return (id, category, short_title, words, medium, genre)
    elif title_SC.match(title):
        m = title_SC.match(title)
        category = 'SC'                         # Spoken Contex-Governed
        (short_title, words, medium, genre) = m.groups()
        return (id, category, short_title, words, medium, genre)
    elif title_SD.match(title):
        category = 'SD'                         # Spoken Demographic
        m = title_SD2.match(title)
        (short_title, no_convsations, recorder, recorderID, date, 
         no_interlocutors, sentences, words) = m.group(1, 2, 3, 4, 5, 6, 7, 8)
        return (id, category, no_convsations, recorder, 
                recorderID, date, no_interlocutors, sentences, words)
    else:
        return (id, 'unidentified')



def containers(s_node):
    """
    for a given s_node, returns a string that indicates its position
    in the document structure of the file.
    """

    def tag_atts2(n):
        atts = []
        atts_string = ''
        tag_string = ''
        for k in n.keys():
            if k == 'level': atts.append(n.get(k))
            elif k == 'type': atts.append(n.get(k))
            elif k == 'n': pass # atts.append('[{0}]'.format(n.get(k)))
            elif k == 'rend': pass
            else: atts.append(k+':'+n.get(k))
        atts_string = ','.join(atts)
        if n.tag == 'div':
            tag_string = ''
        else:
            tag_string = n.tag

        if atts_string == '':
            return tag_string
        else: return '{0}({1})'.format(tag_string, atts_string)

    ancs_node = []
    ancs_str = []
    for n in s_node.iterancestors():
        # if n.tag == "bncDoc": break
        if n.tag == "wtext" or n.tag == "stext": break
        if n.tag == "div": continue
        ancs_node.append(n)
    ancs_node.reverse()

    # ancs_str modifications
    ancs_str = [tag_atts2(x) for x in ancs_node]
    if ancs_str[0].startswith('p(caption'):
        ancs_str[0] = 'caption'
    if len(ancs_str) > 1 and ancs_str[0] == 'p':
        ancs_str = ancs_str[1:]
    
    # head extraction
    head = ancs_str[0].split('(')[0]

    return ('-'.join(ancs_str), head)

# flatten !!!!!!   to be refined

def flatten(e):
    if e.tag == 'w':
        return '_'.join([e.text.strip(), e.attrib['c5'], e.attrib['hw']])
    elif e.tag == 'c':
        return '_'.join([e.text.strip(), e.attrib['c5']])




# for debugging

if __name__ == '__main__':
    for doc in list_W:
        tree = et.parse(abs_path(doc))
        text = tree.xpath('/bncDoc/wtext')[0]
        texttype = text.attrib['type']
        print( doc, texttype, )
        # for child in text.iterchildren():
            # print( child.tag, )
        print
