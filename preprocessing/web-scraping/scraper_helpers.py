import requests
from bs4 import BeautifulSoup
import time


def get_specific_location(soup):
    ps = [item for item in soup.find(class_='content-well').findAll('p') if 'Location' in item.text]
    if len(ps) == 0:
        return None
    else:
        # assert len(ps) == 1
        return ps[0].text


def make_soup(url, url_params=None, timeout=5):
    time.sleep(1)
    r = requests.get(url, params=url_params, timeout=timeout)
    html_doc = r.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    return soup


def get_content(soup, case_enquiry_id):
    if type(case_enquiry_id) != int:
        case_enquiry_id = int(case_enquiry_id)

    d = {
        'case_enquiry_id': case_enquiry_id,
        'title': None,
        'description': None,
        'specific_location': None
    }

    try:
        h2_text = soup.find(class_='content-head').h2.text
    except AttributeError:
        print case_enquiry_id
        raise Exception

    if h2_text != 'Report not available':
        d['title'] = h2_text
        d['description'] = soup.find(class_='content-well').blockquote.p.text
        d['specific_location'] = get_specific_location(soup)

    return d


if __name__=='__main__':
    from pprint import pprint

    for REPORT_NUM in [101000295613]:
        soup = make_soup('https://311.boston.gov/reports/{}'.format(REPORT_NUM))
        pprint(get_content(soup, int(REPORT_NUM)))