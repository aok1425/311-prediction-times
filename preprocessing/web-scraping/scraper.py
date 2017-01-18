# I tried threading. Gave up when there were errors w chunk_size=3 and sleep=2.

from timeit import Timer
from scraper_helpers import get_content, make_soup
import threading
from collections import deque # bc thread-safe # https://docs.python.org/2/library/collections.html#deque-objects
import pandas as pd
import time
from tqdm import trange, tqdm

# from pymongo import MongoClient


POOL_SIZE = 4
API_HOST = "https://311.boston.gov/reports/"

DB_NAME = "yelp"
COLLECTION_NAME = "business"

# client = MongoClient()
# db = client[DB_NAME]
# coll = db[COLLECTION_NAME]


coll = deque()

# def get_cases_parallel(case_id):
#     """
#     Retrieves the JSON response that contains the top 20 business meta data for city.
#     :param case_id: city name
#     """
#     # this was gonna be used for multiprocessing, but i didn't end up using it
#     assert type(case_id) == str
#     case_id = int(float(case_id))
#     response = get_case(case_id)
#     coll.append(response)


def get_case(case_id):
    """
    Makes a request to Yelp's search API given the city name.
    :param case_id:
    :return: dict meta data for issue/case
    """
    # this one actually appends to d
    soup = make_soup(API_HOST + str(case_id))
    d = get_content(soup, case_id)
    coll.append(d)


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


if __name__ == '__main__':
    FILE_PATH = 'case_enquiry_ids_head.csv'
    FILE_PATH = 'case_enquiry_ids.csv'

    t2 = Timer(lambda: scrape_parallel_concurrent(FILE_PATH, chunk_size=10))
    print "Completed parallel in %s seconds." % t2.timeit(1)

    # scrape_sequential('case_enquiry_ids_head.csv')
    finished_case_ids = set([item['case_enquiry_id'] for item in coll])

    case_ids = get_case_ids(FILE_PATH, ignore_header=True)

    print '### Going over all the missed case_ids...'
    for case_id in tqdm(case_ids):
        case_id = int(float(case_id))

        if case_id not in finished_case_ids:
            get_case(case_id)

    export_deque_to_pkl(coll)
    print 'PKL made'

    make_csv_from_pkl()
    print 'CSV made'
