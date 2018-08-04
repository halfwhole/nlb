import grequests
import gevent
from bs4 import BeautifulSoup
from collections import defaultdict

BASE_BRN_URL = "http://catalogue.nlb.gov.sg/cgi-bin/spydus.exe/ENQ/EXPNOS/BIBENQ?BRN="

def read_records(book_records):
    return [str(book_record['brn']) for book_record in book_records]

def build_available_books_dictionary(brn_list):
    """
    Returns a dictionary, where a key = an available book, its value = list of (library, call number) tuples where the book is available.
    The dictionary HAS NOT been filtered for specified libraries, as listed in libs.txt.
    """
    def make_brn_soups(brn_list):
        brn_urls = list(map(lambda brn: BASE_BRN_URL + brn, brn_list))
        rs = (grequests.get(brn_url) for brn_url in brn_urls)
        requests = grequests.map(rs)
        brn_soups = []
        for request in requests:
            response = request.content.decode(request.encoding)
            brn_soup = BeautifulSoup(response, "html5lib")
            brn_soups.append(brn_soup)
        return brn_soups

    def query_brn_title(brn_soup):
        try:
            return brn_soup.findAll("table")[2].find("tr").findAll("td")[2].get_text()
        except:
            raise Exception("Could not parse the catalogue webpage for the book's title")

    def query_brn_records(brn_soup):
        try:
            rows = brn_soup.findAll("table")[-1].find("tbody").findAll("tr")[1:]
            rows_available = filter(lambda row: row.findAll("td")[-1].get_text() == 'Available', rows)
            records_available = list(map(lambda row: (row.find("td").get_text(), row.findAll("td")[2].get_text(" ")), rows_available))
            return records_available
        except:
            raise Exception("Could not parse the catalogue webpage for the book's records")

    avail_books_dict = {}
    brn_soups = make_brn_soups(brn_list)
    for brn_soup in brn_soups:
        brn_title = query_brn_title(brn_soup)
        brn_records = query_brn_records(brn_soup)
        if brn_records:
            avail_books_dict[brn_title] = brn_records

    return avail_books_dict

def build_available_libs_dictionary(avail_books_dict):
    """
    Returns a dictionary, where a key = a library, its value = list of (title, call number) tuples for available books in the library.
    The dictionary HAS NOT been filtered for specified libraries, as listed in libs.txt.
    """
    avail_libs_dict = defaultdict(list)
    for title, libs in avail_books_dict.items():
        for lib, call_number in libs:
            avail_libs_dict[lib].append((title, call_number))
    return dict(avail_libs_dict)

def get_libs_dict(book_records):
    brn_list = read_records(book_records)
    avail_books_dict = build_available_books_dictionary(brn_list)
    avail_libs_dict  = build_available_libs_dictionary(avail_books_dict)
    return avail_libs_dict
