#!/usr/bin/env python

import os
from itertools import repeat
from datetime import datetime
import xapian

from .format import TEXT_FIELDS, DATA_FIELDS, SLOT_FIELDS
from .format import PREFIXES, SLOT_VALUES


def norm(v: str) -> str:
    return (v.strip().lower().replace(" ", "_"))


# common
def get_stemmer():
    return xapian.Stem("en")


# for indexing documents
def get_termgen():
    termgen = xapian.TermGenerator()
    termgen.set_stemmer(get_stemmer())
    return termgen


# for locating documents
def get_queryparser(db=None):
    queryparser = xapian.QueryParser()
    queryparser.set_stemmer(get_stemmer())
    queryparser.set_stemming_strategy(xapian.QueryParser.STEM_SOME)
    if db is not None:
        queryparser.set_database(db)
    return queryparser


def make_query(data):
    qp = get_queryparser()
    text_fields = TEXT_FIELDS.intersection(data.keys())
    Qs = []
    Qs.append(xapian.Query.MatchAll)
    for text_field in text_fields:
        tfq = map(qp.parse_query,
                  data[text_field],
                  repeat(xapian.QueryParser.FLAG_DEFAULT),
                  repeat(PREFIXES[text_field]))
        tfq = xapian.Query(xapian.Query.OP_OR, tuple(tfq))
        Qs.append(tfq)
    data_fields = DATA_FIELDS.intersection(data.keys())
    for data_field in data_fields:
        normed = map(norm, data[data_field])
        dfq = map(''.join, zip(repeat(PREFIXES[data_field]), normed))
        dfq = map(xapian.Query, dfq)
        dfq = xapian.Query(xapian.Query.OP_OR, tuple(dfq))
        Qs.append(dfq)
    slot_fields = SLOT_FIELDS.intersection(data.keys())
    for slot_field in slot_fields:
        if slot_field == 'posted_after':
            value = datetime.strptime(data[slot_field], "%Y-%m-%d").timestamp()
            value = xapian.sortable_serialise(value)
            sfq = xapian.Query(xapian.Query.OP_VALUE_GE,
                               SLOT_VALUES[slot_field],
                               value)
            Qs.append(sfq)
        elif slot_field == 'salary_min':
            value = xapian.sortable_serialise(data[slot_field])
            max_salary = SLOT_VALUES['salary_max']
            sfq = xapian.Query(xapian.Query.OP_VALUE_GE, max_salary, value)
            Qs.append(sfq)
        elif slot_field == 'salary_max':
            value = xapian.sortable_serialise(data[slot_field])
            min_salary = SLOT_VALUES['salary_min']
            sfq = xapian.Query(xapian.Query.OP_VALUE_LE, min_salary, value)
            Qs.append(sfq)
    return xapian.Query(xapian.Query.OP_AND, tuple(Qs))


def search(q_dict, page_no=0, page_size=12):
    query = make_query(q_dict)
    xdb = xapian.Database(os.getenv('XAPIAN_ROOT'), xapian.DB_OPEN)
    inquiry = xapian.Enquire(xdb)
    inquiry.set_query(query)
    default_sort_slot = SLOT_VALUES['date_posted']
    inquiry.set_sort_by_relevance_then_value(default_sort_slot, True)
    offset = 0 + page_no*page_size
    mset = inquiry.get_mset(offset, page_size)
    hashes = tuple(m.document.get_data().decode('utf-8') for m in mset)
    xdb.close()
    return hashes


if __name__ == '__main__':
    Q = {'title': ('data',),
         'country': ('US',), }
    results = search(Q, page_no=2)
    print(results)
