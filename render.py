import string

def render(template,env):
	return string.Template(template).safe_substitute(env)

### NEW ### EXPERIMENTAL
import re
from util import join, flag

# TODO  $$x  ${x|y|z}???
def render2(template,env):
	# variables
	varnames = re.findall('[$]{?(\w+)}?',template)
	vre = join(set(varnames),"|","(?<![$])[$]{{?{0}}}?")
	def mapper(x):
		s = x.group()
		name = s.replace('$','').replace('{','').replace('}','') # TODO FIX performance
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

if __name__=="__main__":
	template = "to jest $aa test $bb mechanizmu $cc ok ${aa} $$bb $start-zz :) $end-zz"
	out = render(template,dict(aa=12,bb=34))
	out2 = render2(template,dict(aa=12,bb=34,zz=1))
	print(out)
	print(out2)
