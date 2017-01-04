import sys
import re

from render import render
from util import flag

# TODO frame.args sa renderowane podczas budowy ramki w proc nie trzeba ich znowu renderowac

class Frame:
	path = []
	vars = {} # name -> value
	defaults = {} # proc.name -> value
	
	def __init__(self):
		self.id = ''
		self.level = 0
		self.parent = None
		self.name = '__main__'
		self.args = []
		self.args_dict = {}
		self.mods = []
		self.line = 0
		self.filename = '__TODO__'
		self.vars['smash'] = sys.path[0]
		self.init_args_dict()
		
	def child(self, cid, name, args=[], mods=[], line=0, filename=''):
		f = Frame()
		f.id = self.id+'.'+str(cid) if self.id else str(cid)
		f.name = name
		f.level = self.level + 1
		f.parent = self
		f.args = args
		f.mods = mods
		f.line = line
		f.filename = filename
		f.init_args_dict()
		return f

	def render(self, text):
		return render(text, self) # TODO missing values
	
	def args_iter(self,query='',startswith=False): # TODO not used
		for k,v in self.args:
			if query:
				if startswith:
					if k.startswith(query):
						yield k,self.render(v)
				else:
					if k==query:
						yield k,self.render(v)
			else:
				yield k,self.render(v)
				
	def arg(self,name,default='',alt=''):
		alternatives = alt.split(' ')
		for k,v in self.args:
			if k==name or k in alternatives:
				if type(v) is str:
					return self.render(v)
				else:
					return v
		v = self.defaults.get(self.parent.name+'.'+name,default)
		try:
			return self.render(v)
		except:
			return v

	def init_args_dict(self):
		self.args_dict = {}
		for k,v in self.args:
			self.args_dict[k] = v
			
	def get(self, name, default='', split=None):
		out = self.arg(name,self.vars.get(name,default))
		if split != None:
			out = re.split(split,out.strip())
		return out
	__getitem__= get
	
	def get_flag(self, name, default=''):
		return flag(self.get(name, default))

if __name__ == "__main__":
	f=Frame()
	print(re.split('\s+','a b  c'))
	