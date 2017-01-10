# Job Definition Language

from collections import deque
import sys
import os

import parse
from frame import Frame
import proc
import mods

def run_path(path):
	code = open(path,'r').read()
	run_str(code,path)

def run_str(text,filename=''):
	root = Frame()
	frame = root
	# TODO refactor with proc.py -> other
	sections = parse.sections(text)
	line_info = parse.section_line_numbers(text)
	data = [(ln,sn,s) for (ln,sn),s in zip(line_info, sections)]
	steps = [(s,frame.child(id,sn,line=ln,filename=filename)) for x,(ln,sn,s) in enumerate(data)]
	# 
	run_steps(steps)

def run_steps(steps):
	"run steps - list of (section,frame) tuples"
	todo = deque(steps)
	while todo:
		section,frame = todo.popleft()
		name = parse.name(section)
		if not mods.should_run(section,frame):
			continue # TODO log info
		if name=='python':
			proc.python(section,frame)
		elif name=='none':
			pass
		else:
			steps = proc.other(name,section,frame)
			todo.extendleft(reversed(steps))

# TODO refactor with run_steps
def run_frame(frame):
	section = ''
	name = frame.name
	if not mods.should_run(section,frame):
		return # TODO log info
	if name=='python':
		proc.python(section,frame,frame.args)
	elif name=='none':
		pass
	else:
		steps = proc.other(name,section,frame,frame.args)
		run_steps(steps)

def run_autoinit(dirpath):
	aipath = os.path.join(dirpath,'autoinit.smash')
	exists = os.path.exists(aipath)
	if exists:
		run_path(aipath)	

if __name__=="__main__":
	# TODO option to disable autoinit
	path = sys.argv[1]
	dirpath = os.path.split(path)[0] # TODO TEST
	run_autoinit(dirpath)
	run_path(path)
