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

class SERDE:
	"serialization-deserialization interface"
	def __init__(self,kind=''):
		if kind=='':
			ser = self.no_ser
			de = self.no_de
		elif kind=='pickle':
			ser = self.pickle_ser
			de = self.pickle_de
			self.protocol = 3
		elif kind=='json':
			ser = self.json_ser
			de = self.json_de
		self.serialize = ser
		self.deserialize = de
	###
	def json_ser(self,v):
		return json.dumps(v)
	def json_de(self,v):
		return json.loads(v)
	###
	def pickle_ser(self,v):
		return pickle.dumps(v,self.protocol)
	def pickle_de(self,v):
		return pickle.loads(v)
	###
	def no_ser(self,v):
		return v
	def no_de(self,v):
		return v


class LINK:
	"link interface"
	def __init__(self):
		self.cursor.execute('create table if not exists tkv_link (link,k1,k2,ts)')
		self.cursor.execute('create unique index if not exists i_tkv_link1 on tkv_link (link,k1,k2)')
		self.cursor.execute('create index if not exists i_tkv_link2 on tkv_link (link,k2)')
	def add_link(self,link,k1,k2):
		ts = time()
		self.cursor.execute('insert or replace into tkv_link values (?,?,?,?)', (link,k1,k2,ts))
	def get_linked(self,link,k1):
		for x in self.cursor.execute('select k2 from tkv_link where link=? and k1=?',(link,k1)):
			yield x[0]
	def get_linked_to(self,link,k2):
		for x in self.cursor.execute('select k1 from tkv_link where link=? and k2=?',(link,k2)):
			yield x[0]
	def get_links(self,link):
		for x in self.cursor.execute('select k1,k2 from tkv_link where link=?',(link,)):
			yield x
	def delete_links(self,k,any=[],left=[],right=[]):
		for link in any:
			self.cursor.execute('delete from tkv_link where link=? and (k1=? or k2=?)',(link,k,k))
		for link in left:
			self.cursor.execute('delete from tkv_link where link=? and k1=?',(link,k))
		for link in right:
			self.cursor.execute('delete from tkv_link where link=? and k2=?',(link,k))


# TODO separate file + attach
class HIST:
	"history interface"
	def __init__(self):
		self.cursor.execute('create table if not exists tkv_hist (t,k,v,ts)')
		self.cursor.execute('create index if not exists i_tkv_hist on tkv (t,k,ts)')
	def set(self,t,k,v,ts):
		val = self.serialize(v)
		self.cursor.execute('insert into tkv_hist values (?,?,?,?)',(t,k,val,ts))
class NOHIST:
	def __init__(self): pass
	def set(self,t,k,v,ts): pass


# TODO
class STAR:
	"star schema interface"
	def __init__(self):
		self.cursor.execute('create table if not exists tkv_star (s,k1,k2,k3,k4,k5,k6,k7,k8,k9)')
	def add_fact(self,star,*keys):
		pass


# TODO HIST,SERDE mixin
class TKV(SERDE,LINK,NOHIST):
	"Table-Key-Value database"
	def __init__(self,path=':memory:',serde='pickle'):
		self.connection = sqlite3.connect(path)
		self.cursor = self.connection.cursor()
		self.cursor.execute('create table if not exists tkv (t,k,v,ts)')
		self.cursor.execute('create unique index if not exists i_tkv on tkv (t,k)')
		SERDE.__init__(self,serde)
		LINK.__init__(self)
		NOHIST.__init__(self)
	### GET ###
	def get(self,t,k,default=None):
		results = self.cursor.execute('select v from tkv where t=? and k=?',(t,k))
		x = results.fetchone()
		return self.deserialize(x[0]) if x else default
	def __getitem__(self,x):
		return self.get(*x)
	### SET ###
	def set(self,t,k,v):
		ts = time()
		val = self.serialize(v)
		self.cursor.execute('insert or replace into tkv values (?,?,?,?)',(t,k,val,ts))
		super().set(t,k,v,ts)
	def __setitem__(self,x,v):
		self.set(*x,v)
	### ITER ###
	def keys(self,t):
		for k in self.cursor.execute('select distinct k from tkv where t=?',(t,)):
			yield k[0]
	def values(self,t):
		for v in self.cursor.execute('select distinct v from tkv where t=?',(t,)):
			yield self.deserialize(v[0])
	def items(self,t):
		for k,v in self.cursor.execute('select distinct k,v from tkv where t=?',(t,)):
			yield k,self.deserialize(v)
	### OTHER ###
	def delete(self,t,k):
		self.cursor.execute('delete from tkv where t=? and k=?',(t,k))
	def truncate(self,t):
		self.cursor.execute('delete from tkv where t=?',(t,))
	def commit(self):
		self.connection.commit()
	### ### ###
connect = TKV


if __name__=="__main__":
	db = connect(serde='json')
	if 1:
		db.set('usr',1,'bob')
		db.set('usr',2,'alice')
		db.set('usr',3,'charlie')
		db.add_link('usr:knows:usr',1,2)
		db.add_link('usr:knows:usr',1,3)
		db.add_link('usr:knows:usr',2,3)
		#~ print(dict(db.items('usr')))
		#~ print(list(db.get_linked('usr:knows:usr',1)))
		#~ print(list(db.get_links('usr:knows:usr')))
		#~ db.delete_links(2,left=['usr:knows:usr'])
		#~ print(list(db.get_links('usr:knows:usr')))
		#~ print(list(db.values('usr')))
		db['usr',4] = 'david'
		print(db['usr',4])
	if 0:
		CNT = 1000000
		t0=time()
		for i in range(CNT):
			db.set('test',i,str(i))
		dt = time()-t0
		print("db.set {0} elements -> {1:0.1f}s {2:0.0f}/s".format(CNT,dt,CNT/dt))
		t0=time()
		for i in range(CNT):
			db.get('test',i)
		dt = time()-t0
		print("db.get {0} elements -> {1:0.1f}s {2:0.0f}/s".format(CNT,dt,CNT/dt))
