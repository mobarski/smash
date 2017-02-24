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

class KV(S):
	"Key-Value database"
	def __init__(self,path=':memory:'):
		super().__init__()
		conn = sqlite3.connect(path)
		c = conn.cursor()
		c.execute('''create table if not exists kv (k,v,ts)''')
		c.execute('''create unique index if not exists i_kv on kv (k)''')
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


class KCV(S):
	"Key-Column-Value database, similar to Columnar databases"
	def __init__(self,path=':memory:'):
		super().__init__()
		conn = sqlite3.connect(path)
		c = conn.cursor()
		c.execute('''create table if not exists kcv (k,c,v,ts)''')
		c.execute('''create unique index if not exists i_kcv on kcv (k,c)''')
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

class TKCV(S):
	"Table-Key-Column-Value database, similar to Document databases"
	def __init__(self,path=':memory:'):
		super().__init__()
		conn = sqlite3.connect(path)
		c = conn.cursor()
		self.connection = conn
		self.cursor = c
		c.execute('create table if not exists tkcv (t,k,c,v,ts)')
		c.execute('create unique index if not exists i_tkcv on tkcv (t,k,c)')
		c.execute('create table if not exists tkcv_link (t1,link,t2,k1,k2,ts)')
		c.execute('create unique index if not exists i_tkcv_link on tkcv_link (t1,link,t2,k1,k2)')
	### GET ###
	def get(self,t,k,c,default=None):
		results = self.cursor.execute('select v from tkcv where t=? and k=? and c=?',(t,k,c))
		x = results.fetchone()
		return self.deserialize(x[0]) if x else default
	def get_all(self,t,k,default=None):
		results = self.cursor.execute('select c,v from tkcv where t=? and k=?',(t,k))
		x = results.fetchall()
		y = [(c,self.deserialize(v)) for c,v in x]
		return dict(y)
	def get_some(self,t,k,cols,default=None):
		if type(cols)==str: cols=cols.split(' ')
		q_marks = ','.join(['?']*len(cols))
		results = self.cursor.execute('select c,v from tkcv where t=? and k=? and c in (%s)'%(q_marks),[t,k]+list(cols))
		x = results.fetchall()
		y = [(c,self.deserialize(v)) for c,v in x]
		return dict(y)
	### SET ###
	def set(self,t,k,c,v):
		val = self.serialize(v)
		self.cursor.execute('insert or replace into tkcv values (?,?,?,?,?)',(t,k,c,val,time()))
	def set_dict(self,t,k,**kwargs):
		ts = time()
		items = [(t,k,c,self.serialize(v),ts) for c,v in kwargs.items()]
		self.cursor.executemany('insert or replace into tkcv values (?,?,?,?,?)',items)
	### OTHER ###
	def keys(self,t):
		for x in self.cursor.execute('select distinct k from tkcv where t=?',(t,)):
			yield x[0]
	def delete(self,t,k):
		self.cursor.execute('delete from tkcv where t=? and k=?',(t,k))
		# TODO delete links
	def truncate(self,t):
		self.cursor.execute('delete from tkcv where t=?',(t,))
		# TODO delete links
	### LINK ###
	def add_link(self,t1,verb,t2,k1,k2):
		ts = time()
		self.cursor.execute('insert or replace into tkcv_link values (?,?,?,?,?,?)', (t1,verb,t2,k1,k2,ts))
	def get_linked(self,t1,verb,t2,k1):
		for x in self.cursor.execute('select k2 from tkcv_link where t1=? and link=? and t2=? and k1=?',(t1,verb,t2,k1)):
			yield x[0]
	def get_linked_to(self,t1,verb,t2,k2):
		for x in self.cursor.execute('select k1 from tkcv_link where t1=? and link=? and t2=? and k2=?',(t1,verb,t2,k2)):
			yield x[0]

#~ class CDFV(S):
	#~ "Collection-Document-Field-Value database"
	#~ def __init__(self,path=':memory:'):
		#~ super().__init__()
		#~ conn = sqlite3.connect(path)
		#~ c = conn.cursor()
		#~ c.execute('''create table if not exists cdfv (c,d,f,v,ts)''')
		#~ c.execute('''create unique index if not exists i_cdfv on cdfv (c,d,f)''')
		#~ self.connection = conn
		#~ self.cursor = c
	#~ def keys(self,c):
		#~ for x in self.cursor.execute('select distinct d from cdfv where c=?',(c,)):
			#~ yield x[0]
	#~ def set(self,c,d,f,v):
		#~ val = pickle.dumps(v,self.protocol)
		#~ self.cursor.execute('insert or replace into cdfv values (?,?,?,?,?)',(c,d,f,val,time()))
	#~ def get(self,c,d,f,default=None):
		#~ results = self.cursor.execute('select v from cdfv where c=? and d=? and f=?',(c,d,f))
		#~ x = results.fetchone()
		#~ return pickle.loads(x[0]) if x else default
	#~ def get_dict(self,c,d,default=None):
		#~ results = self.cursor.execute('select f,v from cdfv where c=? and d=?',(c,d))
		#~ x = results.fetchall()
		#~ y = [(f,pickle.loads(v)) for f,v in x]
		#~ return dict(y)
	#~ def set_dict(self,c,d,**kwargs):
		#~ ts = time()
		#~ items = [(c,d,f,pickle.dumps(v,self.protocol),ts) for f,v in kwargs.items()]
		#~ self.cursor.executemany('insert or replace into cdfv values (?,?,?,?,?)',items)

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
	db.set('usr',1,'name','alice')
	db.set('usr',2,'name','bob')
	db.set('usr',3,'name','charlie')
	db.add_link('usr','knows','usr',1,2)
	db.add_link('usr','knows','usr',1,3)
	db.add_link('usr','knows','usr',2,3)
	print(list(db.get_linked_to('usr','knows','usr',3)))

if 0:
	db = TKCV()
	db.set('usr',1,'age',12)
	db.set('usr',1,'name','bob')
	print(db.get_some('usr',1,'age xxx name'))
	db.truncate('usr')
	print(db.get_some('usr',1,'name xxx age'))

if 0:
	CNT = 1000000
	db = TKCV('test.db')
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
