import re
from pprint import pprint
from textwrap import dedent
import io
import sys

from render import render

#######################################################

p_sections = "(?xms) ^ \[ .+? (?= ^\[ | \Z)"
p_name = "^\[([^\]]*)\]"
p_name_or_empty = """(?xm)
	(?: ^\[ ([^\]]*) \] ) | 	# section name
	(?: $ )				# new line
"""
p_argt = """(?xms)
	^ ($left) $white (?:
		(?: 	(<<<) $white $eol ($right_many) $end_many ) |
		(?: 	(=|<<) $white ($right_many) $end_many ) |
		(?: 	(<) $white ($right_one) $white $eol )
	)
"""
p_arg = render(p_argt,dict(
	left = r"[^=<\r\n]*?",
	right_one = r"[^\r\n]*?",
	right_many = r".+?",
	white = r"[ \t]*",
	eol = r"(?=[\r\n]|\Z)+",
	end_many = r"(?=^\S|\Z)"
))

def sections(text):
	return re.findall(p_sections,text)

def name(section):
	return re.findall(p_name,section)[0]

def args(section, allowed=[]):
	var_list_7 = re.findall(p_arg,section)
	#print(var_list_7)
	var_list_3 = [(m[0], m[1] or m[3] or m[5], m[2] or m[4] or m[6]) for m in var_list_7]
	def mapper(args): # TODO render in = and < ???
		k,op,v = args
		if allowed and k not in allowed:
			return None,None
		if re.findall(p_sections,k): k=''
		if op=='<<<':
			sio = io.StringIO()
			sys.stdout = sio
			exec(dedent(v),globals(),locals()) # python3
			#exec dedent(v) in globals(),locals() # python2
			sys.stdout = sys.__stdout__
			sio.seek(0)
			return k,sio.read()
		elif op=='<<':
			return k,eval(v.strip())
		elif op=='=':
			return k,dedent(v).lstrip() # TODO smart rstrip
		elif op=='<':
			return k,open(v,'r').read()
	var_list = [(k,v) for k,v in map(mapper,var_list_3) if k!=None]
	#print('DEBUG',name(section),var_list)
	return var_list

def section_line_numbers(text):
	line_number = 1
	out = []
	for name in re.findall(p_name_or_empty, text):
		if name:
			out += [(line_number, name)]
			line_number -= 1 # prevent double counting newline after section name
		line_number += 1
	return out
