# TODO merge with dbpool

import sqlite3

def sql_create(tab,cols,col_type={}):
	out = ""
	out += "drop table if exists {0};\n"
	out += "create table {0} (\n"
	out = out.format(tab)
	for c in cols:
		t = col_type.get(c,'str')
		out += "  {0} {1},\n".format(c,t)
	out = out[:-2]+"\n);\n"
	return out

def sql_insert(tab,col_cnt):
	return "insert into %s values (%s);\n" % (tab,','.join(['?']*col_cnt))

