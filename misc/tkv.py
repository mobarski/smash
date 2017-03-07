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
		elif kind=='json':
			self.ser = self.json_ser
			self.de = self.json_de
	### only first level of dict keys is fixed
	def json1_ser(self,v):
		if type(v)==dict:
			val = ['dict', list(v.items())]
		else:
			val = v
		return json.dumps(val,separators=(',',':'))
	def json1_de(self,v):
		val = json.loads(v)
		if type(val)==list and len(val)==2 and val[0]=='dict':
			return dict(val[1])
		else:
			return val
	###
	def json_ser(self,v):
		return json.dumps(v,separators=(',',':'))
	def json_de(self,v):
		val = json.loads(v)
		return _fix_json_keys(val)
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
def _fix_json_keys(val):
	if type(val)==list:
		return list(map(_fix_json_keys,val))
	elif type(val)==dict:
		if len(val)>0 and list(val.keys())[0].isnumeric():
			return dict(zip(map(int,val.keys()),map(_fix_json_keys,val.values())))
		else:
			return dict(zip(val.keys(),map(_fix_json_keys,val.values())))
	return val


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
# TODO query
class HIST:
	"history interface"
	def __init__(self,kind='no'):
		if kind in ('','no','none'):
			self.hist_set = self.no_set
			self.hist_del = self.no_del
			self.no_init()
		elif kind=='tab':
			self.hist_set = self.tab_set
			self.hist_del = self.tab_del
			self.tab_init()
		elif kind.startswith('file:'):
			self.hist_set = self.file_set
			self.hist_del = self.file_del
			filepath = kind[5:]
			self.file_init(filepath)
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
	###
	def file_init(self,filepath):
		self.hist_f = open(filepath,'a')
	def file_set(self,t,k,v,ts):
		val = self.ser(v)
		rec = t,'set',k,val,ts
		rec_ser = str(rec)
		self.hist_f.write(rec_ser+'\n')
		self.hist_f.flush()
	def file_del(self,t,k):
		rec = t,'del',k,'',ts
		rec_ser = str(rec)
		self.hist_f.write(rec_ser+'\n')
		self.hist_f.flush()

class STAR:
	"star schema interface via Table-Partition-Value database"
	def __init__(self):
		self.conn.execute('create table if not exists tpv (t,p,v)')
		self.conn.execute('create index if not exists i_tpv on tpv (t,p)')
	def add(self,t,p,v):
		part = self.ser(p)
		val = self.ser(v)
		self.conn.execute('insert into tpv values (?,?,?)',(t,part,val))
	def all(self,t,p=''): # TODO rename to part, and add all method for accessing all items
		part = self.ser(p)
		for x in  self.conn.execute('select v from tpv where t=? and p=?',(t,part)):
			yield self.de(x[0])
	### AUX - TPV ###
	def drop(self,t,p):
		part = self.ser(p)
		self.conn.execute('delete from tpv where t=? and p=?',(t,part))
	### CORE - STAR ###
	def add_fact(self,t,k_list,v,p=''):
		self.add(t,p,[list(k_list),v])
	def star_join(self,k_list,spec):
		for t,k in zip(spec.split(' '),k_list):
			if t != '_':
				yield self.get(t,k)
	def star_filter(self,star,spec,f_list=[],p=''): # TEST
		for k_list,v in self.all(star,p):
			ok = True
			for d,f in zip(self.star_join(k_list,spec),f_list):
				if not f(d):
					ok = False
					break
			if ok:
				yield k_list,v
		# TODO ??? f.func_code.co_varnames[0]
		# TODO ??? yield func(k_list,v)
	### AUX - STAR ###

class DICT:
	"dict-like object interface"
	def tab_as_dict(self,t):
		class KV:
			def __getitem__(s,k): return self.get(t,k)
			def __setitem__(s,k,v): return self.set(t,k,v)
			def __len__(s): return self.len(t)
			def keys(s): return self.keys(t)
			def values(s): return self.values(t)
			def items(s): return self.items(t)
		return KV()
	def link_as_dict(self,link,default=None):
		class KV:
			def __getitem__(s,k): return self.get_link(link,k[0],k[1],default)
			def __setitem__(s,k,v): return self.set_link(link,k[0],k[1],v)
			# TODO: change to single link iters
			def __len__(s): return self.len(link)
			def keys(s): return self.keys(link)
			def values(s): return self.values(link)
			def items(s): return self.items(link)
		return KV()
	def fact_as_dict(self,t,p=''):
		class KV:
			#def __getitem__(s,k): return self.get_link(link,k[0],k[1],default)
			def __setitem__(s,k,v): return self.add_fact(t,k,v,p)
			#def __len__(s): return self.len(link)
			#def keys(s): return self.keys(link)
			#def values(s): return self.values(link)
			def items(s): return self.all(t,p)
		return KV()


class TKV(SERDE,LINK,HIST,STAR,DICT):
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
		DICT.__init__(self)
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
			yield self.de(k),self.de(v)
	def len(self,t):
		for x in self.conn.execute('select count(1) from tkv where t=?',(t,)):
			return x[0]
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
	db = connect(serde='json',hist='file:hist.txt')
	if 1: # TEST dict
		if 1:
			usr = db.tab_as_dict('usr')
			usr[1] = 'alice'
			usr[2] = 'bob'
			usr[3] = 'charlie'
			print(list(db.items('usr')))
			print(len(usr))
		if 1:
			likes = db.link_as_dict('likes',0)
			likes[1,1] = 1
			likes[1,3] = -1
			likes[2,2] = 1
			likes[3,3] = 1
			print(likes[1,5])
			print(list(likes.items()))
		if 0:
			vv = db.fact_as_dict('vidview')
			vv[1,1,1] = 1
			vv[1,2,1] = 2
			vv[1,3,3] = 3
			vv[2,2,2] = 4
			vv[3,1,2] = 5
			vv[3,2,3] = 6
			print(list(vv.items()))
			print(list(db.all('vidview')))
			
	if 0: # TEST star
		db.set('usr',1,'alice')
		db.set('usr',2,'bob')
		db.set('usr',3,'charlie')
		db.set('asset',1,'aliens')
		db.set('asset',2,'mad max')
		db.set('asset',3,'star wars')
		db.set('device',1,'pc')
		db.set('device',2,'phone')
		db.set('device',3,'tablet')
		###
		db.add_fact('vidview',[1,1,1],1)
		db.add_fact('vidview',[1,2,1],2)
		db.add_fact('vidview',[1,3,3],3)
		db.add_fact('vidview',[2,2,2],4)
		db.add_fact('vidview',[3,1,2],5)
		db.add_fact('vidview',[3,2,3],6)
		###
		print(list(db.star_filter('vidview','usr',[lambda x:x in ['bob','charlie']])))
		print(list(db.star_filter('vidview','usr',[lambda x:x=='alice'])))
		print(list(db.star_filter('vidview','usr',[lambda x:1])))
		print(list(db.star_filter('vidview','usr',[lambda x:0])))
		print(list(db.star_filter('vidview','usr',[])))
		print(lambda x:x.usr in ['bob',''] and x.dev=='pc')
		print(lambda x: x['usr'] in ['bob',''] and x['dev']=='pc')
		print("x.usr in ['bob',''] and x.dev=='pc'")
		#print(list(db.star_filter('vidview','usr',lambda usr:usr in ['bob','charlie']])))
	if 0:
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
		print(list(db.star_join([1,2,3,4,5],'usr _ usr')))
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
