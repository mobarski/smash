## DECLARATIVE AUTOMATION SHELL
## (c) 2017 by mobarski (at) gmail (dot) com
## licence: MIT
## version: mk2

## mk2 CHANGES:
## - text after section name -> section hint (one line description)
## - dedent code before splitting it into sections
## - ability to select lines based on first character (to pass metadata in comments)
## - default value changed from None to empty string 

import re
from textwrap import dedent

# TODO rename parse
# TODO rename cnt -> cols -> col_cnt
# TODO multiline cells -> how ???
# TODO control over stripping cells 
# TODO complex types ???

p_section = """ (?xms)
	^ \*{3} \s* (.+?) \s* \*{3}	# name
	[ \t]* (.*?) [ \t]* $			# meta
	(.+?) (?= ^ \*{3} | \Z)		# body
"""

def parse(text,cnt=0,default='',comments='#<>!@+-*|',empty='.',select=''):
	"parse body of dash section and return list of values for each row"
	def field(x):
		return x.strip() if x.strip()!=empty else default
	def fields(line):
		return [field(x) for x in re.split('\t+',line)]

	if select:
		lines = [x.strip() for x in re.split('\n\r|\r\n|\n|\r',text.strip()) if x.strip() and x.strip()[0] in select]
	else:
		lines = [x.strip() for x in re.split('\n\r|\r\n|\n|\r',text.strip()) if x.strip() and x.strip()[0] not in comments]

	if cnt:
		return [(fields(line)+[default]*cnt)[:cnt] for line in lines]
	else:
		return [fields(x) for x in lines]

def sections(text):
	"return [name,hint,body] for each section"
	return re.findall(p_section,dedent(text))

__SCITE_CFG = """
	-- DASH
	file.patterns.diff=$(file.patterns.diff);*.dash
	use.tabs.*.dash=1
	tab.size.*.dash=8
	indent.size.*.dash=8
	fold.flags=0
"""

###################################################

if __name__=="__main__":
	test = """
	*** sekcja ***
		to		jest		test
		raz		2		trzy
		# comment
		wartosc	.		pusta

	*** costam *** xxx
	@	k1	v1
	@	k2	v2
	>	col1	col2	col3
		aaa
	# 	comment
		bbb		zzz
		ccc
	!	zzz	xxx	xxx
		
	"""
	for name,hint,body in sections(test):
		#print(name,parse(body,comment='#',get_comments=False))
		print(name,parse(body))
