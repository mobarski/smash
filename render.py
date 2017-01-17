import string

def render1(template,env):
	return string.Template(template).safe_substitute(env)

### NEW ### EXPERIMENTAL
import re
from util import join, flag

def render2(template,env):
	# variables
	varnames = re.findall('[$]{?(\w+)}?',template) # TODO sort by desc len + unique
	vre = join(varnames+[''],"|","[$]?[$]{{?{0}}}?") # +[''] for handling $$ without var name
	def mapper(x):
		s = x.group()
		if s.startswith('$$'):
			return s[1:] # reduce one dollar sign
		name = s[1:].replace('{','').replace('}','') # TODO one replace operation
		return str(env.get(name,s))
	out = re.sub(vre,mapper,template)
	
	# conditional blocks
	cre = '[$]start-(\w+) (.*?) [$]end-\\1'
	conditionals = re.findall(cre,out,re.X)
	def mapper(x):
		name = x.group(1)
		text = x.group(2)
		return text if flag(env.get(name,'yes')) else ''
	out = re.sub(cre,mapper,out,re.X)
	return out

render = render2

################################################

if __name__=="__main__":
	template = "$$ to jest $aa test $bb mechanizmu $cc ok ${aa} $$bb $start-zz :) $end-zz"
	out = render1(template,dict(aa=12,bb=34))
	out2 = render2(template,dict(aa=12,bb=34,zz=1))
	print(out)
	print(out2)
