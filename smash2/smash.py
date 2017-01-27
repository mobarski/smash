from __future__ import print_function

import parse

from itertools import chain
import traceback
import sys
import os

# TODO env -> fun(stack)
# TODO stack.append(args)
# TODO filename + linenumber

### recursive descent interpreter
### stack - list of frames (dicts)
def run_str(text,stack=[]):
	for section in parse.sections(text):
		run_section(section,stack)

def run_section(text,stack=[]):
	name = parse.name(text)
	# TODO run_mods like skip run but without running python in other arguments
	if name=='python':
		run_python(text,stack)
	else:
		run_other(text,stack)
	# TODO pass ouput / prev

def run_python(text,stack=[]):
	args = parse.args(text)
	#print('\nDEBUG run_python %s %s'%(args,stack))
	def get(key,default=None):
		for k,v in chain.from_iterable([args]+[f['args'] for f in stack]):
			if k==key: return v
		return default
	
	for k,v in args:
		if k=='':
			# TODO refector into separate function
			try:
				# TODO something that works in py2 and py3
				exec(v,globals(),locals()) # python3
				#exec v in globals(),locals() # python2
			except Exception as e:
				e_name = e.__class__.__name__
				e_info = e.args[0]
				tb = sys.exc_info()[2]
				e_line = traceback.extract_tb(tb)[-1][1]
				# TODO filename and linenumber
				error = "ERROR: {0} - {1} at line {2}".format(e_name,e_info,e_line)
				print(error,file=sys.stderr)
				#print(v.splitlines()[e_line-1])
				# TODO print call stack
				exit(1)

def run_other(text,stack=[]):
	name = parse.name(text)
	code,path = get_proc_code(name)
	args = parse.args(text)
	#print('\nDEBUG run_other %s %s'%(args,stack))
	frame = dict(name=name,args=args,path=path)
	stack += [frame]
	run_str(code,stack)
	del stack[-1]

def get_proc_code(name):
	default_path = os.path.join(sys.path[0],'proc')
	for proc_path in [default_path]:
		path = os.path.join(proc_path,name+'.smash')
		if os.path.exists(path):
			return open(path,'r').read(),path
	# TODO raise error on not found?
	
### CLI ##########################################

def run_path(path,stack=[]):
	code = open(path,'r').read()
	frame = dict(path=path)
	stack += [frame]
	run_str(code,stack)

def run_autoinit(dirpath,stack=[]):
	aipath = os.path.join(dirpath,'autoinit.smash')
	if os.path.exists(aipath):
		run_path(aipath, stack)

if __name__=="__main__":
	if 0:
		# TODO option to disable autoinit
		try:
			path = sys.argv[1]
		except:
			print("USAGE: python smash.py script.smash")
			exit(1)
		dirpath = os.path.split(path)[0] # TODO TEST
		stack = []
		run_autoinit(dirpath,stack)
		run_path(path,stack)
	
s=[]
run_str("""
[hello]
[hello]
""",s)
print(s)
