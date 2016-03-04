# python 3
# Run though refs.xml file and check if DOI has been deposited

from urllib.request import Request, urlopen
from urllib.error import  URLError
import xml.etree.ElementTree

agent = "10.3403"


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


def doi_from_xml(xml_file):
    out = []
    e = xml.etree.ElementTree.parse(xml_file).getroot()
    for atype in e.findall('item'):
        ref = (atype.find('ref').text)
        id = (atype.find('id').text)
        out.append([ref,id])
    return out


def wt_err(ref, id, err):
    with open('log.txt', 'a') as the_file:
        the_file.write(ref + "|" + id + "|" + err + "\n")

items = doi_from_xml('refs.xml')
for item in items:
    id = item[1]
    ref = item[0]
    print('Checking: ' + id)
    # check = check_doi(str(id))
    # if check is True:
    #     print('OK')
    #     wt_err(ref, id, 'OK')
    # else:
    #     print('ERROR: ' + str(check))
    #     wt_err(ref, id, str(check))
