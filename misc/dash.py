## DECLARATIVE AUTOMATION SHELL
## (c) 2017 by mobarski (at) gmail (dot) com
## licence: MIT

import re

# TODO rename parse
# TODO parse_meta
# TODO parse_comments
# TODO more control over strip
# TODO complex types

p_section = """ (?xms)
	^ \*{3} \s* (.+?) \s* \*{3}		# name
	[ \t]* (.*?) [ \t]* $			# meta
	(.+?) (?= ^ \*{3} | \Z)		# body
"""

def parse(text,cnt=0,default=None,comment='#<>!@+-*|',empty='.',get_comments=False):
	"parse body of dash section and return list of values for each row"
	def field(x):
		return x.strip() if x.strip()!=empty else default
	def fields(line):
		return [field(x) for x in re.split('\t+',line)]

	lines = [x.strip() for x in re.split('\n\r|\r\n|\n|\r',text.strip()) if (x.strip() and x.strip()[0] in comment)==get_comments]

	if cnt:
		return [(fields(line)+[default]*cnt)[:cnt] for line in lines]
	else:
		return [fields(x) for x in lines]

def sections(text):
	"return [name,meta,body] for each section"
	return re.findall(p_section,text)

__SCITE_CFG = """
	-- DASH
	file.patterns.diff=$(file.patterns.diff);*.dash
	use.tabs.*.dash=1
	tab.size.*.dash=8
	indent.size.*.dash=8
"""

###################################################

if __name__=="__main__":
	from textwrap import dedent
	test = """
	*** sekcja ***
		to		jest		test
		raz		2		trzy
		# comment
		wartosc	.		pusta

	*** costam *** xxx
		aaa
	# 	comment
		bbb		zzz
		ccc
	!!	zzz	xxx	xxx
		
	"""
	for name,meta,body in sections(dedent(test)):
		#print(name,parse(body,comment='#',get_comments=False))
		print(name,parse(body))
