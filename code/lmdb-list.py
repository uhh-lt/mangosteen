#!/usr/bin/env python

from __future__ import print_function
import argparse

parser = argparse.ArgumentParser(description='Lists the LMDB databases.')
parser.add_argument('database', help='The name of the database.')
parser.add_argument('-0', action='store_true', help='Print null terminated strings.')
args = vars(parser.parse_args())
end = '\0' if args['0'] else '\n'

import lmdb

DATABASE = '/home/dmitry/lmdb'

env = lmdb.open(DATABASE, max_dbs=1, create=False, readonly=True)
db  = env.open_db(args['database'])

with env.begin(db=db) as txn:
    with txn.cursor() as curs:
        for key, _ in curs:
            print(key, end=end)
