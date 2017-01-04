# Configuration Description Language

import re
from pprint import pprint
#from collections import OrderedDict
from itertools import chain
from textwrap import dedent

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
		(?: 	(=|<) $white ($right_one) $white $eol )
	)
"""
p_arg = render(p_argt,dict(
	left = r"[^=\r\n]+?",
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

def args(section):
	var_list_5 = re.findall(p_arg,section)
	var_list_3 = [(m[0], m[1] or m[3], m[2] or m[4]) for m in var_list_5]
	def mapper(args):
		k,op,v = args
		if op=='<<<':
			return k,dedent(v) # ??? .strip()
		elif op=='=':
			return k,v.strip()
		elif op=='<':
			return k,open(v,'r').read()
	var_list = list(map(mapper,var_list_3))
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
