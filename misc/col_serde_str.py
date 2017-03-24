import re

data = """
>1^20=http://google.com/q=costam
<1
<1+zzz
++xxx
-yyy
N
*2
=http://google.com/q=xxx+costam
$6=yyy
|2
^4=https
"""

def decode(data):
	out = []
	reference = {}
	prev = ''
	rows = [x.strip() for x in re.split('\n',data) if x.strip()]
	for row in rows:
		op,rest=row[0],row[1:]
		if op=='N':
			out+=[None]
			continue
		elif op=='=':	out+=[rest]
		elif op=='+':	out+=[prev+rest]
		elif op=='-':	out+=[prev[:-len(rest)]+rest]
		elif op=='*':	out+=[prev]*int(rest)
		elif op=='|':
			out+=out[-int(rest):]
			continue # DO NOT change prev
		elif op in '$^':
			i = rest.index('=')
			n,v = int(rest[:i]),rest[i+1:]
			if op=='$':
				out += [prev[:-n]+v]
			elif op=='^':
				out += [v+prev[n:]]
		elif op in '>':
			i = rest.index('=')
			x,v = rest[:i],rest[i+1:]
			if '^' in x:
				k,n = x.split('^')
				reference[k] = v[:int(n)]
			else:
				reference[x] = v
			out += [v]
		elif op in '<':
			if rest.isdigit():
				out += [reference[rest]]
			else:
				i = rest.index('+')
				k,v = rest[:i],rest[i+1:]
				out += [reference[k]+v]
		prev = out[-1]
	return out

if __name__=="__main__":
	for x in decode(data):
		print(x)
