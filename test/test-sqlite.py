import sys
sys.path.append('..')
from sqlite import *

##############
if __name__=="__main__":
	data = """
	aa bb cc dd
	11 2.2 3.33 44
	"""
	tab = "moja"
	cols = 'id klucz nazwa costam'

	db = sqlite3.connect('test.db')
	sql=sql_create(tab,bsv.findall(cols))
	db.executescript(sql)

	col_cnt = len(next(bsv.rowiter(data)))
	sql=sql_insert(tab,col_cnt)
	db.executemany(sql,bsv.rowiter(data))

	print(cols)
	for r in db.execute('select * from moja'):
		print(r)