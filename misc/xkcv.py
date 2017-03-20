import sqlite3

# TODO combine attach and create
# TODO (time) partitioned fact tables with specific sort order

# TODO optional column dictionary table (autoindexed)
# TODO benchmark

# TODO optional key dictionary table (autoindexed)
# TODO benchmark

# FIX this approach doesn't work, id/rowid is incremented on replace
class REFTAB1:
	def ref_create(self,t,name):
		self.conn.execute('create table if not exists {0}.{1} (x)'.format(t,name))
		self.conn.execute('create unique index if not exists {0}.i_{1} on {1} (x)'.format(t,name))
	def ref_add(self,t,name,x):
		self.conn.execute('insert or replace into {0}.{1}(x) values (?)'.format(t,name),(x,))
	def ref_list(self,t,name):
		print(list(self.conn.execute('select rowid,x from {0}.{1}'.format(t,name))))

# TODO OPTIMIZE
#from collections import defaultdict
class REFTAB2:
	def __init__(self):
		self.ref = {}
		self.ref_inv = {}
	def ref_create(self,t,name):
		self.ref[t,name] = {}
		self.ref_inv[t,name] = {}
	def ref_get(self,t,name,x):
		if x not in self.ref[t,name]:
			id = len(self.ref[t,name])+1
			self.ref[t,name][x] = id
			self.ref_inv[t,name][id] = x
			return id
		else:
			return self.ref[t,name][x]
	def ref_inv_get(self,t,name,col):
		return self.ref_inv[t,name][col]
	def ref_list(self,t,name):
		print(self.ref[t,name])
		print(self.ref_inv[t,name])
	###
	def set2(self,t,k,c,v):
		col = self.ref_get(t,'cols',c)
		self.conn.execute('insert or replace into {0}.xkcv values (?,?,?)'.format(t),(k,col,v))
	def get2(self,t,k,c,default=None):
		col = self.ref_get(t,'cols',c)
		query = self.conn.execute('select v from {0}.xkcv where k=? and c=?'.format(t),(k,col))
		x = query.fetchone()
		return x[0] if x else default
	def store2(self,t,k,items):
		self.conn.executemany('insert or replace into {0}.xkcv values (?,?,?)'.format(t),[(k,self.ref_get(t,'cols',c),v) for c,v in items])
	def items2(self,t,k):
		for col,v in self.conn.execute('select c,v from xkcv where k=?'.format(t),(k,)):
			yield self.ref_inv_get(t,'cols',col),v
	def columns2(self,t,k):
		for x in self.conn.execute('select c from {0}.xkcv where k=?'.format(t),(k,)):
			yield self.ref_inv_get(t,'cols',x[0])
	def all2(self,t):
		for k in self.keys(t):
			yield k,list(self.items2(t,k))
REFTAB=REFTAB2

class XKCV(REFTAB):
	"eXternaltable-Key-Column-Value database"
	def __init__(self,path=':memory:'):
		self.path=path
		self.conn=sqlite3.connect(path)
		REFTAB.__init__(self)
	### CORE ###
	def attach(self,t,path=''):
		p = path if path else t+'.db'
		self.conn.execute("attach database ? as ?",(p,t))
	def create(self,t,path=''):
		self.attach(t,path)
		self.conn.execute('create table if not exists {0}.xkcv (k,c,v)'.format(t))
		self.conn.execute('create unique index if not exists {0}.i_xkcv on xkcv (k,c)'.format(t))
	def set(self,t,k,c,v):
		self.conn.execute('insert or replace into {0}.xkcv values (?,?,?)'.format(t),(k,c,v))
	def get(self,t,k,c,default=None):
		query = self.conn.execute('select v from {0}.xkcv where k=? and c=?'.format(t),(k,c))
		x = query.fetchone()
		return x[0] if x else default
	### ITER ###
	def store(self,t,k,items):
		self.conn.executemany('insert or replace into {0}.xkcv values (?,?,?)'.format(t),[(k,c,v) for c,v in items])
	def keys(self,t):
		for x in self.conn.execute('select distinct k from {0}.xkcv'.format(t)):
			yield x[0]
	def columns(self,t,k):
		for x in self.conn.execute('select c from {0}.xkcv where k=?'.format(t),(k,)):
			yield x[0]
	def values(self,t,k):
		for x in self.conn.execute('select v from {0}.xkcv where k=?'.format(t),(k,)):
			yield x[0]
	def items(self,t,k):
		for x in self.conn.execute('select c,v from xkcv where k=?'.format(t),(k,)):
			yield x
	def all(self,t):
		for k in self.keys(t):
			yield k,list(self.items(t,k))
	### OTHER ###
	def delete(self,t,k):
		self.conn.execute('delete from {0}.xkcv where k=?'.format(t),(k,))
	def truncate(self,t):
		self.conn.execute('delete from {0}.xkcv'.format(t)) # vacuum?
	def commit(self):
		self.conn.commit()
	### ### ###
connect = XKCV

if __name__=="__main__":
	db = connect()
	db.create('user')
	db.ref_create('user','cols')
	db.set2('user',1,'name','maciek')
	db.set2('user',1,'nick','moki')
	db.set2('user',2,'name','agnieszka')
	db.set2('user',2,'nick','felia')
	db.store2('user',3,[('name','mikolaj'),('nick','miki')])
	print(db.get2('user',1,'name'))
	print(list(db.keys('user')))
	print(list(db.columns2('user',1)))
	print(list(db.values('user',1)))
	print(list(db.items2('user',1)))
	#db.truncate('user')
	print(list(db.all2('user')))
	#db.ref_list('user','cols')
	db.commit()
