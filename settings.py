#! /usr/bin/python
# -*- coding: utf-8 -*-


DATADIR     = './tmp'
ENCODING    = 'utf-8'
SLEEP       = 0.05
QUERIES     = 'queries.txt'


'''
Input remote settings.
If local, replace the following with `REMOTE = None`
'''
#REMOTE = {
#    'ip': '147.46.94.52',
#    'id': '',   # fill me
#    'pw': '',   # fill me
#    'dir': '/data/tmp/pskang/blog'
#}
REMOTE = None

'''
MongoDB Setting,
If you do not want to use mongodb, MONGODB = None
'''
MONGODB = None
#MONGODB = {
#    'MAX_POOL_SIZE' : 50,
#    'port' : 27340,
#    'host' : 'mongodb://localhost',
#    'db' : 'test',
#    'collection' : 'articles'
#}
