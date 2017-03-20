import sqlite3

# TODO RENAME: moget, RandSeqDB

# TODO combine FACT and XKCV
# TODO list interface to FACT: __len__, __iadd__ , append, extend
# TODO dict&set interface to XKCV

# TODO vs:
# - central metadata
# - per table metadata

# TODO combine attach and create
# TODO specific sort order

def slots(values):
	return ','.join(['?']*len(values))

class FACT:
	"FACT database"
	def __init__(self,path=':memory:'):
		self.path=path
		self.conn=sqlite3.connect(path)
	### CORE ###
	def attach(self,t,path=''):
		p = path if path else t+'.db'
		self.conn.execute("attach database ? as ?",(p,t))
	def detach(self,t):
		self.conn.execute("detach database ?",(t,))
	def create(self,t,cols,path=''):
		if ' ' in cols: # TODO fix for single value
			columns = ','.join(cols.split(' '))
		else:
			columns = ','.join(cols)
		self.attach(t,path)
		self.conn.execute('create table if not exists {0}.fact ({1})'.format(t,columns))
	def insert(self,t,values):
		self.conn.execute('insert into {0}.fact values ({1})'.format(t,slots(values)),values)
	def insertmany(self,t,items):
		if len(items)==0: return
		values=items[0]
		self.conn.executemany('insert into {0}.fact values ({1})'.format(t,slots(values)),items)
	def all(self,t):
		for x in self.conn.execute('select * from {0}.fact'.format(t)):
			yield x
	### OTHER ###
	def truncate(self,t):
		self.conn.execute('delete from {0}.fact'.format(t)) # vacuum?
	def commit(self):
		self.conn.commit()
	def count(self,t):
		return self.conn.execute('select count(*) from {0}.fact'.format(t)).fetchone()[0]
	### ### ###

from collections import defaultdict
# TODO staging in :memory:/file, sort data and load into propper partitions
# TODO or list of attached partitions, LRU based detach
class PART(FACT):
	"Partitioned FACT database"
	def __init__(self):
		self.get_part_fun = {}
		self.get_col_names = {}
		self.get_part_list = {}
		FACT.__init__(self)
	def open(self,t):
		self.attach(t) # TODO xkcv
		self.get_col_names[t] = self.conn.execute('select value from {0}.fact where meta="cols"'.format(t)).fetchone()[0]
		self.get_part_fun[t] = eval(self.conn.execute('select value from {0}.fact where meta="pfun"'.format(t)).fetchone()[0])
		self.get_part_list[t] = [] # TODO
	def create(self,t,cols,part_fun='lambda x:x[-1]'):
		self.get_col_names[t] = cols
		self.get_part_fun[t] = eval(part_fun)
		self.get_part_list[t] = []
		# TODO xkcv
		FACT.create(self,t,'meta value')
		self.insert(t,['cols',cols])
		self.insert(t,['pfun',part_fun])
	def create_part(self,t,p):
		tab = '{0}_{1}'.format(t,p)
		cols = self.get_col_names[t]
		FACT.create(self,tab,cols)
		if p not in self.get_part_list[t]:
			self.get_part_list[t] += [p]
			self.get_part_list[t].sort()
		# TODO save partition list?
	def append_part(self,t,p,values):
		self.extend_part(t,p,[values])
	def extend_part(self,t,p,items):
		tab = '{0}_{1}'.format(t,p)
		self.insertmany(tab,items)
	def append(self,t,values):
		self.extend(t,[values])
	def extend(self,t,items): # TODO OPTIMIZE   # TODO controlled spill not only at the end
		part_fun = self.get_part_fun.get(t) or (lambda x:x[-1])
		by_p = defaultdict(list)
		for values in items:
			p = part_fun(values)
			by_p[p] += [values]
		for p in by_p:
			self.create_part(t,p)
		# TODO save partition list
		for p,p_items in by_p.items():
			self.extend_part(t,p,p_items)
	def all(self,t,query,partitions=None):
		if partitions==None:
			part_list = self.get_part_list[t]
		elif ' ' in partitions: # TODO fix for single value
			part_list = partitions.split(' ')
		else:
			part_list = partitions
		sql = ' union all '.join(["select * from {0}_{1}.fact".format(t,p) for p in part_list])
		return 'with {0} as ({1}) {2}'.format(t,sql,query)
connect = PART

if __name__=="__main__":
	db = connect()
	#db.create('emisje','user asset time')
	db.open('emisje')
	db.commit()
	db.append('emisje',('maciek','incepcja','2012'))
	db.commit()
	db.extend('emisje',[('agnieszka','chicago','2010'),('maciek','la la land','2017')])
	print(db.conn.execute(db.all('emisje','select user,time from emisje')).fetchall())
