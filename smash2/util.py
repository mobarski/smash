from functools import partial

import sys

# simple function composition mechanism
def pipe(out,*args):
	for fun in args:
		if callable(fun):
			out = fun(out)
		else: print(out,fun) # TODO partial?
	return out

def sort_by(key=None, reverse=False): return partial(sorted,key=key,reverse=reverse)
def filter_by(key=None): return partial(filter,key)

class echo:
	def __init__(self,a,b,echo=True):
		self.a = a
		self.b = b
		self.echo = echo
	def write(self, data):
		self.a.write(data)
		if self.echo:
			self.b.write(data)

if __name__=="__main__":
	x = echo(sys.stdout,sys.stderr)
	x.write('sss')

