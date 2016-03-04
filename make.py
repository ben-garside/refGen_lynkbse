import datetime
from xml.dom import minidom
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def read_from_log(log_file):
    out = []
    f = open(log_file, 'r')
    for line in f:
        print(line)
        if '\n' == line[-1]:
            line = line[:-1]
        ref, id, status = line.split('|')
        out.append([ref,id])
    return out


def make_xml(items, file_name):
    references = ET.Element("references")
    dt = datetime.datetime.now().strftime('%Y-%m-%d')
    for add_item in items:
            item = ET.SubElement(references,"item")
            ref = ET.SubElement(item,"ref")
            id = ET.SubElement(item,"id")
            ref.text = str(add_item[0])
            id.text = str(add_item[1])
            item.attrib['addedOn'] = dt
    rough_string = ET.tostring(references, "utf-8")
    xml_string = minidom.parseString(rough_string)
    new_xml = xml_string.toprettyxml(indent="\t")
    with open(file_name + '.xml', 'a') as the_file:
        the_file.write(new_xml)


make_xml(read_from_log('ref_ok.txt'),'refs')




