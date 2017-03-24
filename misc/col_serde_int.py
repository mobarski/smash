import re

data = """
@100
~0
+10
*2
N
*2
=200
+1
x2
|5
x1
"""

def decode(data):
	out = []
	base = 0
	p_op,p_v = '',''
	rows = [x.strip() for x in re.split('\n',data) if x.strip()]
	for row in rows:
		op,rest=row[0],row[1:]
		if op=='N':
			out+=[None]
			continue
		else:
			v=int(rest)
		if op=='=':	out+=[v]
		elif op=='~':	out+=[v+base]
		elif op=='+':	out+=[out[-1]+v]
		elif op=='-':	out+=[out[-1]-v]
		elif op=='*':	out+=[out[-1]]*v
		elif op=='|':	out+=out[-v:]
		elif op=='@':	base=v
		elif op=='x':	# TODO refactor
			for i in range(v):
				if p_op=='=':		out+=[p_v]
				elif p_op=='+':		out+=[out[-1]+p_v]
				elif p_op=='-':		out+=[out[-1]-p_v]
				elif p_op=='*':		out+=[out[-1]]*p_v
				elif p_op=='|':		out+=out[-p_v:]	
		p_op,p_v=op,v
	return out

if __name__=="__main__":
	for x in decode(data):
		print(x)
