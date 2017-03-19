from time import time
import sqlite3

# TODO table dictionary
# TODO optional column dictionary

class tk2cv:
	"Table-Key-Key2-Column-Value database"
	def __init__(self,path=':memory:'):
		self.path=path
		self.conn=sqlite3.connect(path)
		self.conn.execute('create table if not exists tk2cv (t,k,k2,c,v)')
		self.conn.execute('create unique index if not exists i_tk2cv on tk2cv (t,k,k2,c)')
	### CORE ###
	def get(self,t,k,k2,c,default=None):
		query = self.conn.execute('select v from tk2cv where t=? and k=? and k2=? and c=?',(t,k,k2,c))
		x = query.fetchone()
		return x[0] if x else default
	def set(self,t,k,k2,c,v):
		self.conn.execute('insert or replace into tk2cv values (?,?,?,?,?)',(t,k,k2,c,v))
	### ITER ###
	def keys(self,t):
		for x in self.conn.execute('select distinct k,k2 from tk2cv where t=?',(t,)):
			yield x
	def columns(self,t,k,k2):
		for x in self.conn.execute('select c from tk2cv where t=? and k=? and k2=?',(t,k,k2)):
			yield x[0]
	def values(self,t,k,k2):
		for x in self.conn.execute('select v from tk2cv where t=? and k=? and k2=?',(t,k,k2)):
			yield x[0]
	def items(self,t,k,k2):
		for x in self.conn.execute('select c,v from tk2cv where t=? and k=? and k2=?',(t,k,k2)):
			yield x		
	def all(self,t):
		for k,k2 in self.keys(t):
			yield k,k2,list(self.items(t,k,k2))
	### OTHER ###
	def store(self,t,k,k2,items):
		data = [(t,k,k2,c,v) for c,v in items]
		self.conn.executemany('insert or replace into tk2cv values (?,?,?,?,?)',data)
	def delete(self,t,k,k2):
		self.conn.execute('delete from tk2cv where t=? and k=? and k2=?',(t,k,k2))
	def truncate(self,t):
		self.conn.execute('delete from tk2cv where t=?',(t,))
	def commit(self):
		self.conn.commit()
	### K2 SPECIFIC ###
	def k2_by_k(self,t,k):
		pass
	def k_by_k2(self,t,k2):
		pass
	def all_by_k(self,t,k):
		pass
	def all_by_k2(self,t,k2):
		pass
	def delete_by_k(self,t,k):
		pass
	def delete_by_k2(self,t,k2):
		pass
	### ### ###
connect = tk2cv

if __name__=="__main__":
	db = connect()
	db.set('user',1,1,'name','maciek')
	db.set('user',1,1,'nick','moki')
	db.set('user',2,2,'name','agnieszka')
	db.set('user',2,2,'nick','felia')
	db.store('user',3,3,[('name','mikolaj'),('nick','miki')])
	print(db.get('user',1,1,'name'))
	print(list(db.keys('user')))
	print(list(db.columns('user',1,1)))
	print(list(db.values('user',1,1)))
	print(list(db.items('user',1,1)))
	print(list(db.all('user')))
