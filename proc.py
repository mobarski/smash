from __future__ import print_function
from pprint import pformat,pprint

import os
import sys
import re

import parse

dyn_proc = dict() # kind -> text

########################

def let_var_name(key):
	match = re.findall('let\s+(\w+)',key)
	if match:
		return match[0]
	return None

def get_proc_code(name,frame=None):
	"returns procedure code and file path"
	# TODO - move to frame vars defaults?
	default_path = os.path.join(sys.path[0],'proc')
	if frame:
		proc_paths = frame.path+[default_path] # TODO
	else:
		proc_paths = [default_path]
	
	for p in proc_paths:
		path = os.path.join(p,name+'.smash')
		#print('checking path '+path) # DEBUG
		if os.path.exists(path):
			return open(path,'r').read(),path
	return dyn_proc[name],'__TODO__'

### BUILTIN PROCEDURES ############################

def python(section,frame,args=[]):
	get = frame.get
	get_flag = frame.get_flag
	args = args or parse.args(section)
	for key,val in args:
		value = frame.render(val)
		if key == 'code':
			code = value
			try:
				exec(code)
			except Exception as e:
				e_str = "{0} {1}".format(e.__class__.__name__, str(e))
				error_msg = []
				f = frame
				while f.parent:
					error_msg.insert(0,"{0}:{1}:{2}: {3}".format(f.filename,f.line,f.name,e_str))
					f=f.parent
				print('\n'.join(error_msg), file=sys.stderr)
				exit(1)
		k = let_var_name(key)
		if k:
			frame.vars[k] = eval(value)
		if key == 'print':
			print(eval(value))
		if key == 'pprint':
			pprint(eval(value))
		if key == 'debug':
			for k in re.split('\s+',value):
				print(k,"=",pformat(get(k)))

def other(proc,section,frame,args=[]):
	raw_args = parse.args(section)
	args = args or [(key,frame.render(val)) for key,val in raw_args]
	code,filename = get_proc_code(proc,frame)
	sections = parse.sections(code)
	line_info = parse.section_line_numbers(code)
	data = [(ln,sn,s) for (ln,sn),s in zip(line_info, sections)]
	steps = [(s,frame.child(x+1,sn,args,line=ln,filename=filename)) for x,(ln,sn,s) in enumerate(data)]
	return steps

if __name__=="__main__":
	print("proc.py:11::zzz")
