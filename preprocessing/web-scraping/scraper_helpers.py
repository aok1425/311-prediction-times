# import requests
from bs4 import BeautifulSoup
import time

import io
import pycurl

SOCKS_PORT = 7000

def get_specific_location(soup):
    ps = [item for item in soup.find(class_='content-well').findAll('p') if 'Location' in item.text]
    if len(ps) == 0:
        return None
    else:
        # assert len(ps) == 1
        return ps[0].text


def query(url, SOCKS_PORT):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """
  output = io.BytesIO()

  query = pycurl.Curl()
  query.setopt(pycurl.URL, url)
  query.setopt(pycurl.PROXY, 'localhost')
  query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
  query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
  query.setopt(pycurl.WRITEFUNCTION, output.write)

  try:
    query.perform()
    return output.getvalue()
  except pycurl.error as exc:
    return "Unable to reach %s (%s)" % (url, exc)


def make_soup(url, url_params=None, timeout=5):
    time.sleep(2)
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
    r = requests.get(url, params=url_params, timeout=timeout, headers=headers)
    html_doc = r.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    return soup


def make_soup(url, *args, **kwargs):
    html_doc = query(url, SOCKS_PORT)
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

<<<<<<< HEAD:preprocessing/web-scraping/scraper_helpers.py
    try:
        h2_text = soup.find(class_='content-head').h2.text
    except AttributeError:
        print case_enquiry_id
        raise Exception

=======
    h2_text = soup.find(class_='content-head').h2.text
>>>>>>> 9c52c9b... now works w Tor! using this on AWS:preprocessing/web-scraping/helper_scrapers.py
    if h2_text != 'Report not available':
        d['title'] = h2_text
        d['description'] = soup.find(class_='content-well').blockquote.p.text
        d['specific_location'] = get_specific_location(soup)

    return d
<<<<<<< HEAD:preprocessing/web-scraping/scraper_helpers.py


if __name__=='__main__':
    from pprint import pprint

    for REPORT_NUM in [101000295613]:
        soup = make_soup('https://311.boston.gov/reports/{}'.format(REPORT_NUM))
        pprint(get_content(soup, int(REPORT_NUM)))
=======
>>>>>>> 9c52c9b... now works w Tor! using this on AWS:preprocessing/web-scraping/helper_scrapers.py
