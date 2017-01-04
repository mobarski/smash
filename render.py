import string

def render(template,env):
	return string.Template(template).safe_substitute(env)

### NEW ### EXPERIMENTAL
import re
from util import join

# TODO $$x  ${x}  ${x|y|z}
def render2(template,env):
	varnames = re.findall('[$](\w+)',template)
	vre = join(varnames,"|","[$]{0}")
	def mapper(x):
		s = x.group()
		return str(env.get(s[1:],s))
	return re.sub(vre,mapper,template)

if __name__=="__main__":
	out = render("to jest $aa test $bb mechanizmu $cc ok",dict(aa=12,bb=34))
	print(out)
