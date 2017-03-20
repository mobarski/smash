import sqlite3

# TODO combine attach and create
# TODO (time) partitioned fact tables with specific sort order

class XKCV:
	"eXternaltable-Key-Column-Value database"
	def __init__(self,path=':memory:'):
		self.path=path
		self.conn=sqlite3.connect(path)
	### CORE ###
	def attach(self,t,path=''):
		p = path if path else t+'.db'
		self.conn.execute("attach database ? as ?",(p,t))
	def detach(self,t):
		self.conn.execute("detach database ?",(t,))
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
	db.set('user',1,'name','maciek')
	db.set('user',1,'nick','moki')
	db.set('user',2,'name','agnieszka')
	db.set('user',2,'nick','felia')
	db.store('user',3,[('name','mikolaj'),('nick','miki')])
	print(db.get('user',1,'name'))
	print(list(db.keys('user')))
	print(list(db.columns('user',1)))
	print(list(db.values('user',1)))
	print(list(db.items('user',1)))
	#db.truncate('user')
	print(list(db.all('user')))
	db.commit()
