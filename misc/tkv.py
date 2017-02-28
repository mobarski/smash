import sqlite3
import pickle
import json
from time import time
from itertools import chain


"""
NoSQL interface to SQLite
"""

# TODO insert old values into history table
# TODO remove ser(key) ???

# PERF no serialization vs pickle -> 1.5 x writes per second, 1.1 x reads per second
# PERF json vs pickle -> 1.3 writes per second, 0.6 reads per second
# PERF optional pickle vs pickle -> 0.9 x reads and writes per second

class SERDE:
	"serialization-deserialization interface"
	def __init__(self,kind=''):
		if kind=='':
			self.ser = self.no_ser
			self.de = self.no_de
		elif kind=='pickle':
			self.ser = self.pickle_ser
			self.de = self.pickle_de
			self.protocol = 3
		elif kind=='json': # ERROR with int keys
			self.ser = self.json_ser
			self.de = self.json_de
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

# doesn't work well with json -> int keys are turned into str keys
class LINK: # dict based
	"link interface for graph databases"
	def __init__(self): pass
	### CORE ###
	def set_link(self,link,k1,k2,v=1):
		d = self.get(link,k1,{})
		if k2 not in d or d[k2]!=v:
			d[k2] = v
			self.set(link,k1,d)
	def get_links(self,link,k1,t=''): # t='' for same api as get_linked
		return self.get(link,k1,{})
	def get_linked(self,link,k1,t):
		for k2 in self.get(link,k1,{}).keys():
			yield self.get(t,k2)
	### AUX 
	def set_links(self,link,k1,links_dict):
		d = self.get(link,k1,{})
		d.update(links_dict)
		self.set(link,k1,d)
	def get_link(self,link,k1,k2,default=None):
		d = self.get(link,k1,{})
		return d.get(k2,default)
	def del_link(self,link,k1,k2):
		d = self.get(link,k1,{})
		if k2 in d:
			del d[k2]
			self.set(link,k1,d)
	def del_links(self,link,k1,k_list):
		d = self.get(link,k1,{})
		for k2 in k_list:
			if k2 in d: del d[k2]
		elf.set(link,k1,d)


# TODO separate file + attach
class HIST:
	"history interface"
	def __init__(self,kind='no'):
		if kind=='no':
			self.hist_set = self.no_set
			self.hist_del = self.no_del
			self.no_init()
		elif kind=='tab':
			self.hist_set = self.tab_set
			self.hist_del = self.tab_del
			self.tab_init()
	###
	def tab_init(self):
		self.conn.execute('create table if not exists tkv_hist (t,op,k,v,ts)')
		self.conn.execute('create index if not exists i_tkv_hist on tkv_hist (t,op,k,ts)')
	def tab_set(self,t,k,v,ts):
		val = self.ser(v)
		self.conn.execute('insert into tkv_hist values (?,?,?,?,?)',(t,'set',k,val,ts))
	def tab_del(self,t,k):
		ts = time()
		self.conn.execute('insert into tkv_hist values (?,?,?,?,?)',(t,'del',k,'',ts))
	###
	def no_init(self): pass
	def no_set(self,t,k,v,ts): pass
	def no_del(self,t,k): pass

# TODO
class STAR:
	"star schema interface"
	def __init__(self):
		self.conn.execute('create table if not exists tkv_fact (t,k,v,ts)')
		self.conn.execute('create index if not exists i_tkv_fact on tkv_fact (t,ts)')
	def add_fact(self,t,dim,v):
		ts = time()
		key = self.ser(dim)
		val = self.ser(v)
		self.conn.execute('insert or replace into tkv_fact values (?,?,?,?)',(t,key,val,ts))
	def star_join(self,dim,spec):
		for t,k in zip(spec.split(' '),dim):
			if t != '_':
				yield self.get(t,k)


class TKV(SERDE,LINK,HIST,STAR):
	"Table-Key-Value database"
	def __init__(self,path=':memory:',serde='json',hist='no'):
		self.path = path
		self.conn = sqlite3.connect(path)
		self.conn.execute('create table if not exists tkv (t,k,v,ts)')
		self.conn.execute('create unique index if not exists i_tkv on tkv (t,k)')
		SERDE.__init__(self,serde)
		HIST.__init__(self,hist)
		LINK.__init__(self)
		STAR.__init__(self)
	### GET ###
	def get(self,t,k,default=None):
		key=self.ser(k)
		results = self.conn.execute('select v from tkv where t=? and k=?',(t,key))
		x = results.fetchone()
		return self.de(x[0]) if x else default
	### SET ###
	def set(self,t,k,v):
		ts = time()
		key=self.ser(k)
		val = self.ser(v)
		self.conn.execute('insert or replace into tkv values (?,?,?,?)',(t,key,val,ts))
		self.hist_set(t,k,v,ts)
	### ITER ###
	def keys(self,t):
		for k in self.conn.execute('select k from tkv where t=?',(t,)):
			yield self.de(k[0])
	def values(self,t):
		for v in self.conn.execute('select v from tkv where t=?',(t,)):
			yield self.de(v[0])
	def items(self,t):
		for k,v in self.conn.execute('select k,v from tkv where t=?',(t,)):
			yield k,self.de(v)
	### OTHER ###
	def delete(self,t,k):
		key=self.ser(k)
		self.conn.execute('delete from tkv where t=? and k=?',(t,key))
		self.hist_del(t,k)
	def truncate(self,t):
		self.conn.execute('delete from tkv where t=?',(t,))
	def commit(self):
		self.conn.commit()
	### ### ###
connect = TKV


if __name__=="__main__":
	db = connect(serde='pickle',hist='tab')
	if 1:
		db.set('usr',1,dict(name='bob'))
		db.set('usr',2,dict(name='alice'))
		db.set('usr',3,dict(name='charlie'))
		db.set_link('u:knows:u',1,2)
		db.set_link('u:knows:u',1,3,{'since':'2001'})
		db.set_link('u:knows:u',2,3)
		#db.set('link:attr',[2,3],4)
		#db.link[2,3] = 'usr:knows:usr'
		#print(set(db.link['usr:knows:usr',:5,'usr']))
		#~ print(dict(db.items('usr')))
		print(list(db.get_links('u:knows:u',1).items()))
		print(list(db.get_linked('u:knows:u',1,'usr')))
		#print(list(db.star_join([1,2,3,4,5],'usr _ usr')))
		#~ print(list(db.get_links('usr:knows:usr')))
		#~ db.delete_links(2,left=['usr:knows:usr'])
		#~ print(list(db.get_links('usr:knows:usr')))
		#~ print(list(db.values('usr')))
		#print(list(db.get_val_linked_to('usr:knows:usr',3,'usr')))
		#for x in db.conn.iterdump(): print(x)
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

