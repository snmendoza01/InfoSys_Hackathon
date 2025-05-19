#!/usr/bin/env python

import argparse
import sys, os, shutil
import json
import urllib, urllib.request, urllib.parse
import configparser
from datetime import datetime
import re

config_file = os.path.expanduser('~/.inspire.conf')
config_defaults = {
    'query': {
        'size': '10'
    },
    'local': {
        'max_num_authors': '5',
        'page_size': '5',
        'display': 'latex-eu',
        'bib_file': os.path.join(os.path.dirname(__file__),
                                    'bibliography', 'references.bib'),
        'pdf_dir': os.path.join(os.path.dirname(__file__),
                                'bibliography', 'bibtex-pdfs'),
        'download_pdf': True
    }
}

def get_records(query: str,
                sort: str = 'mostrecent',
                size: int = 2) -> tuple[list, int]:
    if not query:
        return [], 0
    inspire_result = dict()
    inspire_query = 'https://inspirehep.net/api/literature'
    inspire_query += '?sort={}'.format(sort)
    inspire_query += '&size={:d}'.format(size)
    inspire_query += '&q=' + urllib.parse.quote(query)
    with urllib.request.urlopen(inspire_query) as req:
        inspire_result = json.load(req)
    return inspire_result["hits"]["hits"], inspire_result["hits"]["total"]


def download_pdf(record: dict, dest_file: str, exist_ok: bool = False) -> None:
    if os.path.exists(dest_file) and not exist_ok:
        raise FileExistsError('"{}" already exists'.format(dest_file))
    else:
        #> identifier: https://info.arxiv.org/help/arxiv_identifier_for_services.html
        #> alternatively could consider using the arix API? (seems overkill for now)
        if 'arxiv_eprints' in record['metadata']:
            arxiv_id = record['metadata']['arxiv_eprints'][0]['value']
            #> old style has the category prefix (primary)
            if not re.fullmatch(r'\d+\.\d+', arxiv_id):
                arxiv_id = record['metadata']['arxiv_eprints'][0][
                    'categories'][0] + '/' + arxiv_id
            urllib.request.urlretrieve(
                'http://arxiv.org/pdf/' + arxiv_id + '.pdf', dest_file)
        else:
            raise ValueError('"{}" has no arXiv entry for PDF download'.format(
                record['metadata']['texkeys'][0]))
        

print(type(get_records("supergraph perturbation theory")[0][0]))
print(get_records("supergraph perturbation theory")[0][0].keys())
leng = len(get_records("supergraph perturbation theory")[0][0])
print(leng)
# print([get_records("supergraph perturbation theory")[0][0][i]['id'] for i in range(leng)])