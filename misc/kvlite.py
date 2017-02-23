import sqlite3
import pickle
from time import time

"""
(extended) Key-Value interface to SQLite
"""

# TODO insert old values into history table

class KV:
	"Key-Value database"
	def __init__(self,path=':memory:'):
		self.protocol = 3
		conn = sqlite3.connect(path)
		c = conn.cursor()
		c.execute('''drop table if exists kv''')
		c.execute('''create table kv (k,v,ts)''')
		c.execute('''create unique index i_kv on kv (k)''')
		self.connection = conn
		self.cursor = c
	def keys(self,query='%'):
		for x in self.cursor.execute('select distinct k from kv where k like ?',(query,)):
			yield x[0]
	def set(self,k,v):
		val = pickle.dumps(v,self.protocol)
		self.cursor.execute('insert or replace into kv values (?,?,?)',(k,val,time()))
	def get(self,k,default=None):
		results = self.cursor.execute('select v from kv where k=?',(k,))
		x = results.fetchone()
		return pickle.loads(x[0]) if x else default


class KCV:
	"Key-Column-Value database"
	def __init__(self,path=':memory:'):
		self.protocol = 3
		conn = sqlite3.connect(path)
		c = conn.cursor()
		c.execute('''drop table if exists kcv''')
		c.execute('''create table kcv (k,c,v,ts)''')
		c.execute('''create unique index i_kcv on kcv (k,c)''')
		self.connection = conn
		self.cursor = c
	def keys(self):
		for x in self.cursor.execute('select distinct k from kcv'):
			yield x[0]
	def set(self,k,c,v):
		val = pickle.dumps(v,self.protocol)
		self.cursor.execute('insert or replace into kcv values (?,?,?,?)',(k,c,val,time()))
	def get(self,k,c,default=None):
		results = self.cursor.execute('select v from kcv where k=? and c=?',(k,c))
		x = results.fetchone()
		return pickle.loads(x[0]) if x else default
	def get_dict(self,k,default=None):
		results = self.cursor.execute('select c,v from kcv where k=?',(k,))
		x = results.fetchall()
		y = [(c,pickle.loads(v)) for c,v in x]
		return dict(y)
	def set_dict(self,k,**kwargs):
		ts = time()
		items = [(k,c,pickle.dumps(v,self.protocol),ts) for c,v in kwargs.items()]
		self.cursor.executemany('insert or replace into kcv values (?,?,?,?)',items)


class TKCV:
	"Table-Key-Column-Value database"
	def __init__(self,path=':memory:'):
		self.protocol = 3
		conn = sqlite3.connect(path)
		c = conn.cursor()
		c.execute('''drop table if exists tkcv''')
		c.execute('''create table tkcv (t,k,c,v,ts)''')
		c.execute('''create unique index i_tkcv on tkcv (t,k,c)''')
		self.connection = conn
		self.cursor = c
	def keys(self,t):
		for x in self.cursor.execute('select distinct k from tkcv where t=?',(t,)):
			yield x[0]
	def set(self,t,k,c,v):
		val = pickle.dumps(v,self.protocol)
		self.cursor.execute('insert or replace into tkcv values (?,?,?,?,?)',(t,k,c,val,time()))
	def get(self,t,k,c,default=None):
		results = self.cursor.execute('select v from tkcv where t=? and k=? and c=?',(t,k,c))
		x = results.fetchone()
		return pickle.loads(x[0]) if x else default
	def get_dict(self,t,k,default=None):
		results = self.cursor.execute('select c,v from tkcv where t=? and k=?',(t,k))
		x = results.fetchall()
		y = [(c,pickle.loads(v)) for c,v in x]
		return dict(y)
	def set_dict(self,t,k,**kwargs):
		ts = time()
		items = [(t,k,c,pickle.dumps(v,self.protocol),ts) for c,v in kwargs.items()]
		self.cursor.executemany('insert or replace into tkcv values (?,?,?,?,?)',items)


if 0:
	db = KV()
	db.set('usr:a:age',12)
	db.set('usr:a:name','johan')
	db.set('usr:a:data',[1,2,3])
	db.set('usr:b:age',24)
	db.set('usr:b:age',42)
	db.set('usr:b:name','isaac')

	x=db.get('usr:v:age')
	print(x)
	x=db.get('usr:a:age')
	print(x)
	print(list(db.keys('usr:a:%')))

if 0:
	db = KCV()
	db.set('usr:a','age',12)
	db.set('usr:a','name','johan')
	db.set('usr:a','data',[1,2,3])
	db.set('usr:b','age',24)
	db.set('usr:b','age',42)
	db.set('usr:b','name','isaac')
	db.set_dict('usr:c',a=1,b=2)

	x=db.get('usr:v','age')
	print(x)
	x=db.get_dict('usr:c')
	print(x)
	print(list(db.keys()))

if 1:
	db = TKCV()
	db.set('usr',1,'age',12)
	db.set('usr',1,'name','johan')
	db.set('usr',1,'data',[1,2,3])
	db.set('usr','b','age',24)
	db.set('usr','b','age',42)
	db.set('usr','b','name','isaac')
	db.set_dict('usr','c',a=1,b=2)

	x=db.get('usr','v','age')
	print(x)
	x=db.get_dict('usr','c')
	print(x)
	print(list(db.keys('usr')))
