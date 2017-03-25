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

#######################################

from collections import defaultdict

def prefix_len(a,b):
	i = 0
	for ai,bi in zip(a,b):
		if ai==bi: i += 1
		else:
			return i
	return i

def encode(rows):
	out = ""
	
	prefix = {'':0}
	prev = ''
	freq = defaultdict(int)
	for row in sorted(rows):
		prefix[row] = prefix_len(row,prev)
		prefix[prev] = max(prefix[row],prefix[prev])
		prefix[prev] = max(prefix[row],prefix[prev])
		prev = row
		freq[row] += 1
		# TODO reference wedlug freq

	reference = {}
	for row in rows:
		p_len = prefix[row]
		if p_len:
			p = row[:p_len]
			if p in reference:
				if p_len<len(row):
					line = '<{0}+{1}'.format(reference[p],row[p_len:])
				else:
					line = '<{0}'.format(reference[p])
			else:
				i = len(reference)+1
				if p_len<len(row):
					line = '>{0}^{1}={2}'.format(i,p_len,row)
				else:
					line = '>{0}={1}'.format(i,row)
				reference[p] = str(i)
		else:
			line = '='+row
		out += line+'\n'
	return out

#######################################

if __name__=="__main__":
	if 0:
		for x in decode(data):
			print(x)
	if 1:
		print(encode(['ala','ma','kota','ala','ma','psa']))
		e = encode([x.strip() for x in """
			http://google.com/q=maciek
			http://google.com/q=warszawa
			https://onet.pl/vod/costam/odcinek/1
			https://google.com/q=test
			http://player.pl/costam/s01/e01
			http://google.com/q=psy
			https://google.com/q=zupa
			http://google.com/q=maciek
			cos od czapy
			xxx
			cos
		""".split('\n') if x.strip()])
		print(e)
		for x in decode(e):
			print(x)

