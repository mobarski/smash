"""
Blank Separated Values
"""

import re

p_row = """(?x) "[^"]*" | '[^']*' | \S+ """
re_row = re.compile(p_row)

def rowiter(text):
	for line in text.splitlines():
		line = line.strip()
		if not line: continue
		yield re_row.findall(line)

def findall(text):
	return re_row.findall(text)

def format(row,sep=' '):
	def reformat(x):
		if type(x)==type(''):
			if re.search('\s',x):
				return "'%s'"%x
			elif re.search("'",x):
				return '"%s"'%x
			else:
				return x
		else:
			return str(x)
	return sep.join(map(reformat,row))

if __name__=="__main__":
	print(format(['a',1,4.2,-3,'b c',"d'"]))
	
