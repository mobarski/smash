import parse
import proc

# TODO "native" proc type, "python" is "native" for this implementation?

def as_flat_list(text):
	out = []
	steps = parse.steps(text)
	for s in steps:
		if s.proc=='python':
			out += [s]
		else:
			proc_text = proc.get(s.proc)
			out += as_flat_list(proc_text)
	return out

def as_tree(text): return '#TODO'

def as_list(text): return '#TODO'

print(as_flat_list("""
[test]
x=1
"""))
