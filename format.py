#!/usr/bin/env python

TEXT_FIELDS = set(('title', 'industry', 'company', 'location',))
DATA_FIELDS = set(('employment_type', 'job_location_type',
                   'language', 'det_language', 'country',
                   'region', 'city', 'salary_currency'))
SLOT_FIELDS = set(('posted_after', 'date_posted', 'salary_min', 'salary_max',))
VIEW_FIELDS = set(('sortby', 'offset',))
PREFIXES = {
    'title': 'A',
    'industry': 'B',
    'company': 'C',
    'employment_type': 'D',
    'job_location_type': 'E',
    'language': 'F',
    'det_language': 'G',
    'country': 'H',
    'region': 'I',
    'city': 'J',
    'location': 'K',
    'salary_currency': 'L'
}
SLOT_VALUES = {'date_posted': 0,
               'posted_after': 0,
               'salary_min': 1,
               'salary_max': 2, }
