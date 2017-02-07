import parse
import proc

def as_flat_list(text):
	out = []
	steps = parse.steps(text)
	for s in steps:
		if s.proc=='python':
			out += [s]
		else:
			proc_text = proc.get(s.proc)
			out += flatten(proc_text)
	return out

print(as_flat_list("""
[test]
x=1
"""))
