class XO(object):
	def __add__(self,b): return lambda a:a+b
	def __sub__(self,b): return lambda a:a-b
	
X=XO()

print(list(map(X-1,[1,2,3])))
