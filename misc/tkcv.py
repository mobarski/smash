from time import time
import sqlite3

# TODO table dictionary
# TODO optional column dictionary

class TKCV:
	"Table-Key-Column-Value database"
	def __init__(self,path=':memory:'):
		self.path=path
		self.conn=sqlite3.connect(path)
		self.conn.execute('create table if not exists tkcv (t,k,c,v)')
		self.conn.execute('create unique index if not exists i_tkcv on tkcv (t,k,c)')
	### CORE ###
	def get(self,t,k,c,default=None):
		query = self.conn.execute('select v from tkcv where t=? and k=? and c=?',(t,k,c))
		x = query.fetchone()
		return x[0] if x else default
	def set(self,t,k,c,v):
		self.conn.execute('insert or replace into tkcv values (?,?,?,?)',(t,k,c,v))
	### ITER ###
	def keys(self,t):
		for x in self.conn.execute('select distinct k from tkcv where t=?',(t,)):
			yield x[0]
	def columns(self,t,k):
		for x in self.conn.execute('select c from tkcv where t=? and k=?',(t,k)):
			yield x[0]
	def values(self,t,k):
		for x in self.conn.execute('select v from tkcv where t=? and k=?',(t,k)):
			yield x[0]
	def items(self,t,k):
		for x in self.conn.execute('select c,v from tkcv where t=? and k=?',(t,k)):
			yield x		
	def all(self,t):
		for k in self.keys(t):
			yield k,list(self.items(t,k))
	### OTHER ###
	def delete(self,t,k):
		self.conn.execute('delete from tkcv where t=? and k=?',(t,k))
	def truncate(self,t):
		self.conn.execute('delete from tkcv where t=?',(t,))
	def commit(self):
		self.conn.commit()
	### ### ###
connect = TKCV

if __name__=="__main__":
	db = connect()
	db.set('user',1,'name','maciek')
	db.set('user',1,'nick','moki')
	db.set('user',2,'name','agnieszka')
	db.set('user',2,'nick','felia')
	print(db.get('user',1,'name'))
	print(list(db.keys('user')))
	print(list(db.columns('user',1)))
	print(list(db.values('user',1)))
	print(list(db.items('user',1)))
	print(list(db.all('user')))
