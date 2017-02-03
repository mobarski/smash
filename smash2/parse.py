import re
from textwrap import dedent

#######################################################

p_sections = "(?xms) ^ \[ .+? (?= ^\[ | \Z)"
p_name = "^\[([^\]]*)\]"
p_name_or_empty = """(?xm)
	(?: ^\[ ([^\]]*) \] ) | 	# section name
	(?: $ )				# new line
"""
p_arg_template = """(?xms)
	(?:	^ ({left}) 	{white} ({op}) {white} 	({right_many}) 	{end_many}	) |
	(?:	^ ({section}) 	{white} (        ) 		({right_many}) 	{end_many}	) |
	(?:	^ ({section}) 	{white} (        )		({right_one}) 		{white} {eol}	)
"""

p_arg = p_arg_template.format(
	op = r"<<<|>>>|<<|>>|<|>|==|=",
	left = r"[^=<\r\n]*?",
	right_one = r"[^\r\n]*?",
	right_many = r".+?",
	white = r"[ \t]*",
	eol = r"(?=[\r\n]|\Z)+",
	end_many = r"(?=^\S|\Z)",
	section = r"\[[^\]]+\]"
)

def _sections(text):
	return re.findall(p_sections,text)

def _name(section):
	return re.findall(p_name,section)[0]

def _args(section):
	groups = re.findall(p_arg,section)
	key_op_val= [(max(g[0::3]),max(g[1::3]),max(g[2::3])) for g in groups]
	def fix(x):
		k,op,v = x
		if re.findall(p_name,k): k=''
		if op=='': op='='
		# TODO fix multiline -> ends with single newline
		# TODO fix multiline -> dedent
		# TODO fix singleline -> strip
		return k,op,v
	return [fix(x) for x in key_op_val]

def _section_line_numbers(text):
	line_number = 1
	out = []
	for name in re.findall(p_name_or_empty, text):
		if name:
			out += [(line_number, name)]
			line_number -= 1 # prevent double counting newline after section name
		line_number += 1
	return out

#######################################################

def parse(text):
	return [(_name(s),_args(s)) for s in _sections(text)] # TODO line numbers
