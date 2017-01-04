import re

def flag(value):
	"convert value to integer bool type"
	s = str(value).strip().lower()
	is_true = s in "yes y true t on 1".split(' ')
	return int(is_true)

def join(lst,dlm='',fmt="{0}",strip=True):
	if strip:
		lst = [x.strip() if hasattr(x,"strip") else x for x in lst]
	return dlm.join([fmt.format(x) for x in lst])

# TODO pipetools clone NEW SANDBOX
class pipe(object):
	def __pipe__(self,*args,**kwargs):
		print("__pipe__",args,kwargs)
	def __call__(self,*args,**kwargs):
		print("__call__",args,kwargs)
###

def _sub(x,fmt):
	a = re.subn('[$][$]','_#D0LaR#_',fmt)[0]
	b = re.subn('[$]',x,a)[0]
	c = re.subn('_#D0LaR#_','$',b)[0]
	return c

def get(name,split=None,join=None,fmt=None):
	raw = "1  2   \r\n 3 4" # TODO
	if split == None:
		after_split = raw
	elif callable(split):
		after_split = split(raw)
	elif type(split) == str:
		after_split = re.split(split, raw)
	else:
		raise
	if fmt == None:
		after_fmt = after_split
	else:
		after_fmt = [_sub(x,fmt) for x in after_split]
	if join == None:
		after_join = after_fmt
	else:
		after_join = join.join(after_fmt)
	return after_join

if __name__=="__main__":
	#print(get('x','\s+','\n,','string(s.$) as new_$'))
	#print(flag('off'))
	pass
