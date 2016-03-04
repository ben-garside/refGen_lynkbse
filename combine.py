# python 3
# Run though refs.xml file and check if DOI has been deposited

from urllib.request import Request, urlopen
from urllib.error import URLError
import os
import itertools
import datetime
from xml.dom import minidom
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


xml_extract_dir = 'extracts'
agent = "10.3403"
list_series = []
list_dated = []
list_undated = []
list_items = []
list_items_to_add = []
list_ref_all = []
list_refs_refs = []


def get_xml_files():
    global list_dated, list_series, list_undated
    files = os.listdir(xml_extract_dir)
    if files:
        for file in files:
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".xml":
                if filename.startswith('standard_series_'):
                    list_series.append(file)
                elif filename.startswith('standards_dated_'):
                    list_dated.append(file)
                elif filename.startswith('standards_undated_'):
                    list_undated.append(file)
        return True
    return False


def get_doi_parts(doi):
    return doi.split("/")


def check_doi(doi):
    if len(doi):
        url = "http://api.crossref.org/works/" + agent + "/" + doi + "/agency"
        req = Request(url)
        try:
            urlopen(req)
        except URLError as e:
            if hasattr(e, 'code'):
                return e.code
        else:
            return True
    return 'noDOI'


def wt_log(ref, id, msg):
    with open('combinelog.txt', 'a') as the_file:
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        the_file.write(dt + "|" + ref + "|" + id + "|" + msg + "\n")


def get_items_series():
    global list_items
    for file in list_series:
        file = xml_extract_dir + '/' + file
        tree = ET.parse(file)
        root = tree.getroot()
        for elem in root.findall('.//{http://www.crossref.org/schema/4.3.6}standard'):
            ref = elem.find('.//{http://www.crossref.org/schema/4.3.6}std_designator').text
            id = elem.find('.//{http://www.crossref.org/schema/4.3.6}doi').text
            list_items.append(([ref,  get_doi_parts(id)[1]]))


def get_items_dated():
    global list_items
    for file in list_dated:
        file = xml_extract_dir + '/' + file
        tree = ET.parse(file)
        root = tree.getroot()
        for elem in root.findall('.//{http://www.crossref.org/schema/4.3.6}standard'):
            ref = elem.find('.//{http://www.crossref.org/schema/4.3.6}std_designator').text
            id = elem.find('.//{http://www.crossref.org/schema/4.3.6}doi').text
            list_items.append(([ref,  get_doi_parts(id)[1]]))


def get_items_undated():
    global list_items
    for file in list_undated:
        file = xml_extract_dir + '/' + file
        tree = ET.parse(file)
        root = tree.getroot()
        for elem in root.findall('.//{http://www.crossref.org/schema/4.3.6}standard'):
            ref = elem.find('.//{http://www.crossref.org/schema/4.3.6}std_designator').text
            id = elem.find('.//{http://www.crossref.org/schema/4.3.6}doi').text
            list_items.append([ref,  get_doi_parts(id)[1]])
            # check for adopted from
            adopt = elem.findall('.//{http://www.crossref.org/schema/4.3.6}std_adopted_from')
            for std in adopt:
                list_items.append([std.text,  get_doi_parts(id)[1]])


def get_doi_from_refs(refs_file):
    global list_ref_all
    e = ET.parse(refs_file)
    root = e.getroot()
    for atype in root.findall('item'):
        addedOn = atype.attrib['addedOn']
        ref = (atype.find('ref').text)
        id = (atype.find('id').text)
        list_ref_all.append([ref,id,addedOn])
        list_refs_refs.append(ref)



def get_doi_to_add():
    global list_dated, list_items, list_items_to_add, list_series, list_undated
    # find all xml files in dir
    get_xml_files()

    # if we have series files...
    if list_series:
        get_items_series()

    # if we have dated files...
    if list_dated:
        get_items_dated()

    # if we have undated files...
    if list_undated:
        get_items_undated()

    # order and remove duplicates
    list_items.sort()
    list_items = list(list_items for list_items,_ in itertools.groupby(list_items))

    # loop through all new items
    for item in list_items:
        dt = datetime.datetime.now().strftime('%Y-%m-%d')
        print('Checking: ' + item[0] + "|" + item[1])
        # check if ref is already in refs.xml file
        if not item[0] in list_refs_refs:
            # this is a new ref...
            # check if DOI has been deposited
            doi = check_doi(item[1])
            # doi = True
            if doi is True:
                print('OK')
                item.append(dt)
                list_items_to_add.append(item)
            else:
                print('DOI error')
                # item.append('DOI-404')
                # list_items_error.append(item)
                wt_log(item[0], item[1], 'DOI-404')
        else:
            # ref already in file
            print('Already in refs')
            # item.append('Already in refs.xml')
            # list_items_error.append(item)
            wt_log(item[0], item[1], 'Already in refs.xml')


if __name__ == "__main__":
    file_name = 'testOut'
    dt = datetime.datetime.now().strftime('%Y-%m-%d')
    # get ref items
    print('getting refs.xml items')
    get_doi_from_refs('refs.xml')
    # get new items
    print('getting new items')
    get_doi_to_add()
    # make root element
    print('lets make the XML')
    # extent list for new and old
    list_items_to_add.extend(list_ref_all)
    references = ET.Element("references")
    references.attrib['generatedOn'] = dt
    # generate XML for new items
    for add_item in list_items_to_add:
        item = ET.SubElement(references,"item")
        ref = ET.SubElement(item,"ref")
        id = ET.SubElement(item,"id")
        ref.text = str(add_item[0])
        id.text = str(add_item[1])
        item.attrib['addedOn'] = add_item[2]
    # pretty print the XML
    rough_string = ET.tostring(references, "utf-8")
    xml_string = minidom.parseString(rough_string)
    new_xml = xml_string.toprettyxml(indent="\t")
    # write the XML file
    with open(file_name + "_" + dt + '.xml', 'a') as the_file:
        the_file.write(new_xml)