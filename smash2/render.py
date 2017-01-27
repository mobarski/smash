import string

def render(template,env):
	return string.Template(template).safe_substitute(env)

if __name__=="__main__":
	env = dict(a=1,b=2,c='a')
	print(render("$a ${b} $$c $d",env))
	print("{a} {b} {c} {d}".format(**env))
