# I tried threading. Gave up when there were errors w chunk_size=3 and sleep=2.

from timeit import Timer
from scraper_helpers import get_content, make_soup
import threading
from collections import deque # bc thread-safe # https://docs.python.org/2/library/collections.html#deque-objects
import pandas as pd
import time
from tqdm import trange, tqdm

from pymongo import MongoClient
import multiprocessing
from time import sleep

import stem.process
from stem import Signal
from stem.control import Controller
from stem import CircStatus


POOL_SIZE = 2
API_HOST = "https://311.boston.gov/reports/"
SOCKS_PORT = 7000


# http://stackoverflow.com/questions/34733562/change-tor-ip-from-python-with-stem
def getIP():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate()
        for circ in controller.get_circuits()[-1:]:
            if circ.status != CircStatus.BUILT:
                continue

            exit_fp, exit_nickname = circ.path[-1]

            exit_desc = controller.get_network_status(exit_fp, None)
            exit_address = exit_desc.address if exit_desc else 'unknown'

            print "Last exit relay:", exit_nickname, exit_address
            # print ("  fingerprint: %s" % exit_fp)
            # print ("  nickname: %s" % exit_nickname)
            # print ("  address: %s" % exit_address)


def set_new_ip():
    """Change IP using TOR"""
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)

DB_NAME = "yelp"
COLLECTION_NAME = "business"


def get_done_case_ids():
    mongo_client = MongoClient(connect=False)
    coll = mongo_client['311']['done']
    done_ids = coll.distinct('case_enquiry_id')
    mongo_client.close()
    return frozenset(done_ids)


coll = deque()


def get_case(case_id):
    """
    Makes a request to Yelp's search API given the city name.
    :param case_id:
    :return: dict meta data for issue/case
    """
    # this one actually appends to d
    soup = make_soup(API_HOST + str(case_id))
    if soup.text == 'throttled':
        print 'Skipping this iteration bc throttled'
        return None
    elif len(soup.text) < 400:
        print case_id
        print soup.text
        return None
    elif soup is None:
        print 'soup {} returns None'.format(case_id)
        return None

    d = get_content(soup, case_id)
    coll.append(d)

    mongo_client = MongoClient(connect=False)
    db = mongo_client['311']['done']
    db.insert_one(d)
    mongo_client.close()


def case_info_concurrent(case_ids):
    """
    Extracts the business ids from the JSON object and
    retrieves the business data for each id concurrently.
    :param json_response: JSON response from the search API.
    """
    threads = []

    for case_id in case_ids:
        t = threading.Thread(target=get_case, args=[case_id])
        threads += [t]

        t.start()

    for t in threads:
        t.join()


def make_filtered_case_ids(file_path, chunk_size):
    case_ids = get_case_ids(file_path, ignore_header=True)
    len_case_ids = len(case_ids)
    print len_case_ids, 'rows'
    done_case_ids = get_done_case_ids()
    len_done_case_ids = len(done_case_ids)
    print len_done_case_ids, 'already done'
    print len_case_ids - len_done_case_ids, 'left to do'

    result = []

    for case_id in case_ids:
        t = threading.Thread(target=get_case, args=[case_id])
        threads += [t]

        t.start()

    for t in threads:
        t.join()

    yield result # for the very last one


def open_file_in_chunks(file_path, chunk_size=5, ignore_header=True):
    with open(file_path) as f:
        if ignore_header:
            f.next()

        try:
            while True:
                chunk = []
                for _ in range(chunk_size):
                    chunk += [f.next()]
                yield chunk
        except StopIteration:
            pass


def scrape_parallel_concurrent(file_path, chunk_size):
    """
    Uses multiple processes to make requests to the search API.
    :param pool_size: number of worker processes
    """
    # NB: overwriting this to be threading, not multiprocessing
    file_chunk_generator = open_file_in_chunks(file_path, chunk_size)

    try:
        for _ in trange(10**10):
            next_chunk = file_chunk_generator.next()
            case_ids = [int(float(i)) for i in next_chunk]
            case_info_concurrent(case_ids)
            # time.sleep(5)
    except StopIteration:
        pass


def get_case_ids(file_path, ignore_header):
    with open(file_path) as f:
        if ignore_header:
            return f.readlines()[1:]
        else:
            return f.readlines()


def scrape_sequential(file_path, ignore_header=True):
    case_ids = get_case_ids(file_path, ignore_header)

    for case_enquiry_id in tqdm(case_ids):
        case_enquiry_id = int(float(case_enquiry_id))
        get_case(case_enquiry_id)


def export_deque_to_pkl(d):
    df = pd.DataFrame(list(d))
    df.to_pickle('temp.pkl')


def make_csv_from_pkl():
    df = pd.read_pickle('temp.pkl')
    df.to_csv('test.csv', index=False)


def scrape_sequential(file_path, ignore_header=True):
    case_ids = get_case_ids(file_path, ignore_header=True)
    len_case_ids = len(case_ids)
    print len_case_ids, 'rows'
    done_case_ids = get_done_case_ids()
    len_done_case_ids = len(done_case_ids)
    print len_done_case_ids, 'already done'
    print len_case_ids - len_done_case_ids, 'left to do'

    filtered_case_ids = [i for i in case_ids if i not in done_case_ids]

    for case_enquiry_id in tqdm(filtered_case_ids):
        get_case(case_enquiry_id)


if __name__ == '__main__':
    FILE_PATH = 'case_enquiry_ids_head.csv'
    FILE_PATH = 'case_enquiry_ids.csv'
    POOL_SIZE = 2
    API_HOST = "https://311.boston.gov/reports/"
    SOCKS_PORT = 7000    
    CHUNK_SIZE = 20

    ip_blacklist = []

    filtered_case_id_chunk_generator = make_filtered_case_ids(FILE_PATH, CHUNK_SIZE)

    tor_process = stem.process.launch_tor_with_config(
        config = {
            'SocksPort': str(SOCKS_PORT),
            'ControlPort': '9051'
            }
        )

    for _ in trange(10**3):
        # scrape_sequential(FILE_PATH)
        getIP()                                         
        scrape_parallel_concurrent(FILE_PATH, POOL_SIZE)
        set_new_ip()
        # sleep(60)

    # t1 = Timer(lambda: scrape_sequential(FILE_PATH))
    # print 'Completed sequential in {} seconds.'.format(t1.timeit(1))
    
    # t2 = Timer(lambda: scrape_parallel_concurrent(FILE_PATH, POOL_SIZE))
    # print "Completed parallel in %s seconds." % t2.timeit(1)
    tor_process.kill()  # stops tor