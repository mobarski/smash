in1 = """
[cmd]= ok

[cmd] << 40+2
x << 123*2

[cmd]
<<<
	x = 42
	y = 123
	print(x,y)
	
...	print ok
	

[data] =
	1 2 3
	4 5 6
	7 8 9

[tsv]
head = no
cols = a b c
out >> tab

[insert] << tab
table = mydata
"""

in2 = """
[aaa] <<<
	jest
	test
x = 42
= x 
	123123
	123123
	123123554

[bbb] << x
x = 42

[ccc] = to jest test
x = 42
"""

import sys
sys.path.append('..')
from parse2 import *

if __name__=="__main__":
	if 1:
		for s in sections(in1):
			print('section name:',name(s))
			print('args:',args(s))
			print()