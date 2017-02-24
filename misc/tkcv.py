import sqlite3
import pickle
import json
from time import time


"""
NoSQL interface to SQLite
"""

# TODO insert old values into history table

# PERF no serialization vs pickle -> 1.5 x writes per second, 1.1 x reads per second
# PERF json vs pickle -> 1.3 writes per second, 0.6 reads per second
# PERF optional pickle vs pickle -> 0.9 x reads and writes per second

class S:
	"serialization interface"
	def __init__(self):
		self.protocol = 3
	def serialize(self,v):
		return pickle.dumps(v,self.protocol)
		#return v
	def deserialize(self,v):
		return pickle.loads(v)
		#return v


class LINK:
	"link interface"
	def __init__(self):
		self.cursor.execute('create table if not exists tkcv_link (t1,link,t2,k1,k2,ts)')
		self.cursor.execute('create unique index if not exists i_tkcv_link on tkcv_link (t1,link,t2,k1,k2)')
	def add_link(self,t1,verb,t2,k1,k2):
		ts = time()
		self.cursor.execute('insert or replace into tkcv_link values (?,?,?,?,?,?)', (t1,verb,t2,k1,k2,ts))
	def get_linked(self,t1,verb,t2,k1):
		for x in self.cursor.execute('select k2 from tkcv_link where t1=? and link=? and t2=? and k1=?',(t1,verb,t2,k1)):
			yield x[0]
	def get_linked_to(self,t1,verb,t2,k2):
		for x in self.cursor.execute('select k1 from tkcv_link where t1=? and link=? and t2=? and k2=?',(t1,verb,t2,k2)):
			yield x[0]
	def delete(self,t,k): pass
	def truncate(self,t): pass


class STAR:
	"star schema interface"
	def __init__(self):
		self.cursor.execute('create table if not exists tkcv_star (s,k1,k2,k3,k4,k5,k6,k7,k8,k9)')
	def add_fact(self,star,*keys):
		pass


class HIST:
	"history interface"
	def __init__(self):
		self.cursor.execute('create table if not exists tkcv_hist (t,k,c,v,ts)')
		self.cursor.execute('create index if not exists i_tkcv_hist on tkcv (t,k,c,ts)')
	def set(self,t,k,c,v,ts):
		val = self.serialize(v)
		self.cursor.execute('insert into tkcv_hist values (?,?,?,?,?)',(t,k,c,val,ts))
	def set_dict(self,t,k,kwargs,ts):
		items = [(t,k,c,self.serialize(v),ts) for c,v in kwargs.items()]
		self.cursor.executemany('insert into tkcv_hist values (?,?,?,?,?)',items)


class TKCV(S,LINK,HIST):
	"Table-Key-Column-Value database, similar to Document databases"
	def __init__(self,path=':memory:'):
		self.connection = sqlite3.connect(path)
		self.cursor = self.connection.cursor()
		self.cursor.execute('create table if not exists tkcv (t,k,c,v,ts)')
		self.cursor.execute('create unique index if not exists i_tkcv on tkcv (t,k,c)')
		S.__init__(self)
		LINK.__init__(self)
		HIST.__init__(self)
	### GET ###
	def get(self,t,k,c,default=None):
		results = self.cursor.execute('select v from tkcv where t=? and k=? and c=?',(t,k,c))
		x = results.fetchone()
		return self.deserialize(x[0]) if x else default
	def get_all(self,t,k,default=None):
		"Get column->value dictionary for all columns"
		results = self.cursor.execute('select c,v from tkcv where t=? and k=?',(t,k))
		x = results.fetchall()
		y = [(c,self.deserialize(v)) for c,v in x]
		return dict(y)
	def get_some(self,t,k,cols,default=None):
		"Get column->value dictionary for selected columns"
		if type(cols)==str: cols=cols.split(' ')
		q_marks = ','.join(['?']*len(cols))
		results = self.cursor.execute('select c,v from tkcv where t=? and k=? and c in (%s)'%(q_marks),[t,k]+list(cols))
		x = results.fetchall()
		y = [(c,self.deserialize(v)) for c,v in x]
		return dict(y)
	### SET ###
	def set(self,t,k,c,v):
		ts = time()
		val = self.serialize(v)
		self.cursor.execute('insert or replace into tkcv values (?,?,?,?,?)',(t,k,c,val,ts))
		super().set(t,k,c,v,ts)
	def set_dict(self,t,k,**kwargs):
		ts = time()
		items = [(t,k,c,self.serialize(v),ts) for c,v in kwargs.items()]
		self.cursor.executemany('insert or replace into tkcv values (?,?,?,?,?)',items)
		super().set_dict(t,k,kwargs,ts)
	### OTHER ###
	def keys(self,t):
		for x in self.cursor.execute('select distinct k from tkcv where t=?',(t,)):
			yield x[0]
	def delete(self,t,k):
		self.cursor.execute('delete from tkcv where t=? and k=?',(t,k))
		super().delete(t,k)
	def truncate(self,t):
		self.cursor.execute('delete from tkcv where t=?',(t,))
		super().truncate(t)
	###
connect = TKCV

if __name__=="__main__":
	if 1:
		db = connect('test.db')
		db.set('usr',1,'name','alice')
		db.set('usr',2,'name','bob')
		db.set('usr',3,'name','charlie')
		db.add_link('usr','knows','usr',1,2)
		db.add_link('usr','knows','usr',1,3)
		db.add_link('usr','knows','usr',2,3)
		print(list(db.get_linked_to('usr','knows','usr',3)))

	if 1:
		db = connect('test.db')
		db.set('usr',1,'age',12)
		db.set('usr',1,'name','bob')
		print(db.get_some('usr',1,'age xxx name'))
		db.truncate('usr')
		print(db.get_some('usr',2,'name xxx age'))

	if 0:
		CNT = 1000000
		db = connect('test.db')
		t0=time()
		for i in range(CNT):
			db.set('test',i,'as_str',str(i))
		dt = time()-t0
		print("db.set {0} elements -> {1:0.1f}s {2:0.0f}/s".format(CNT,dt,CNT/dt))
		t0=time()
		for i in range(CNT):
			db.get('test',i,'as_str')
		dt = time()-t0
		print("db.get {0} elements -> {1:0.1f}s {2:0.0f}/s".format(CNT,dt,CNT/dt))

	if 0:
		db.add_fact('zzzz',1,4,5,6,7)
