in1 = """
to jest
opis

[write]
hint = super co ?
path =    c:\katalog\domowy\123    
body <<<
	to jest [pulapka]
	tresc pliku
	
	[pulapka2]

	fajnie co?



[python]
code = print "ok"
print = true
loglevel = 42
body <<<
	a1uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu
	b2xxxxxxxxxxxxxxx

	c3
x=1
[kolejnosc]
a = 1
b <<<
	2

	22
c = 3
d <<<
	4
		44
	444
e = 5
f <<<
	6
	
	66
"""

in2 = """
[aaa]
x = 1
y <<<
	2
z < test-parse.py
[bbb]
[ccc]
"""

import sys
sys.path.append('..')
from parse import *

if __name__=="__main__":
	if 0:
		pprint(section_line_numbers(in1))
	if 0:
		pprint(list(enumerate(sections(in1))))
	if 1:
		for s in sections(in2):
			print(name(s))
			pprint(args(s))
