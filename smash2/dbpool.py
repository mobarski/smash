# TODO merge with sqlite

import re
p_db = "^(\w+)([(].*[)])$"

cache = {} # signature ->

import sqlite3

def connect_sqlite(args):
	return eval('sqlite3.connect'+args)

def connect(text):
	text = text.strip()
	if not text:
		text = "sqlite(':memory:')"
	if text in cache:
		return cache[text]
	name,args = re.findall(p_db,text)[0]
	if name == 'sqlite':
		db = connect_sqlite(args)
	cache[text] = db
	return db
