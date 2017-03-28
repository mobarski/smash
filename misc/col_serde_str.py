import re

# TODO add row to dict using another row or prefix/suffix
# TODO ? numeric as text
# TODO ? date/time

############################################################

# 2 x shorter values -> czy warto?
base_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
base_chars = "0123456789"
def basex_encode(value):
	pass
def basex_decode(text):
	v=base_chars.index(text[0])
	for x in text[1:]:
		v *= len(base_chars)
		v += base_chars.index(x)
	return v
#print (basex_decode('ZZZZZZZZ'))

############################################################

data = """
>1^20=http://google.com/q=costam
1
1+zzz
0
*3
>2=http://google.com/q=xxx+costam
<1122012120
*3
"""

def decode(data):
	out = []
	reference = {'0':None}
	prev = ''
	rows = [x.strip() for x in re.split('\n',data) if x.strip()]
	for row in rows:
		op,rest=row[0],row[1:]
		if op=='#':	continue
		elif op=='=':	out+=[rest]
		elif op=='*':	out+=[prev]*(int(rest)-1)
		elif op in '>':
			i = rest.index('=') # define word
			#i2 = rest.index(':') # TODO define word using another word from dictionary
			#i3 = rest.index('#') # TODO do not output the word, just define it
			x,v = rest[:i],rest[i+1:]
			if '^' in x:
				k,n = x.split('^')
				reference[k] = v[:int(n)]
			else:
				reference[x] = v
			out += [v]
		elif op in base_chars:
			if '+' in row:
				i = row.index('+')
				k,v = row[:i],row[i+1:]
				out += [reference[k]+v]
			else:
				out += [reference[row]]
		elif op=='<':
			for k in rest:
				out += [reference[k]]
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
	len_freq = defaultdict(int)
	for row in sorted(rows):
		prefix[row] = prefix_len(row,prev)
		prefix[prev] = max(prefix[row],prefix[prev])
		prefix[prev] = max(prefix[row],prefix[prev])
		prev = row
		freq[row] += 1
		if row is not None and row!='':
			len_freq[len(row)] += 1
		# TODO reference wedlug freq

	# stats
	if 1:
		all_cnt = len(rows)
		distinct_cnt = len(freq)
		null_cnt = freq.get(None,0)
		empty_cnt = freq.get('',0)
		
		# simplify other calculations
		freq[None] = 0
		freq[''] = 0
		del freq[None]
		del freq['']
		
		min_val = min(freq)
		max_val = max(freq)
		min_val_cnt = freq[min_val]
		max_val_cnt = freq[max_val]
		min_len = min(len_freq)
		max_len = max(len_freq)
		min_len_cnt = len_freq[min_len]
		max_len_cnt = len_freq[max_len]
		max_freq = max(freq.values())
		max_freq_cnt = sum([(1 if x==max_freq else 0) for x in freq.values()])
		max_freq_val = [k for k,v in freq.items() if v==max_freq]
		out += '#{0}={1}\n'.format('A',all_cnt)
		out += '#{0}={1}\n'.format('D',distinct_cnt)
		out += '#{0}={1}\n'.format('N',null_cnt)
		out += '#{0}={1}\n'.format('E',empty_cnt)
		out += '#{0}={1}\n'.format('LV',min_val)
		out += '#{0}={1}\n'.format('HV',max_val)
		out += '#{0}={1}\n'.format('LVC',min_val_cnt)
		out += '#{0}={1}\n'.format('HVC',max_val_cnt)
		out += '#{0}={1}\n'.format('LL',min_len)
		out += '#{0}={1}\n'.format('HL',max_len)
		out += '#{0}={1}\n'.format('LLC',max_len_cnt)
		out += '#{0}={1}\n'.format('HLC',max_len_cnt)
		out += '#{0}={1}\n'.format('ML','') # TODO ML -> median length (excluding empty)
		out += '#{0}={1}\n'.format('AL','') # TODO AL -> average length (excluding empty)
		out += '#{0}={1}\n'.format('HF',max_freq)
		out += '#{0}={1}\n'.format('HFV',max_freq_val[0])
		out += '#{0}={1}\n'.format('HFC',max_freq_cnt)

	reference = {None:'0'}
	repeat_cnt = 0
	prev = ''
	for row in rows:
		if row==prev:
			repeat_cnt += 1
			continue
		elif repeat_cnt>0:
			out += '*'+str(repeat_cnt+1)+'\n'
			repeat_cnt=0
		p_len = prefix[row]
		if p_len:
			p = row[:p_len]
			if p in reference:
				if p_len<len(row):
					line = '{0}+{1}'.format(reference[p],row[p_len:])
				else:
					line = '{0}'.format(reference[p])
			else:
				i = len(reference)
				if p_len<len(row):
					line = '>{0}^{1}={2}'.format(i,p_len,row)
				else:
					line = '>{0}={1}'.format(i,row)
				reference[p] = str(i)
		else:
			line = '='+row
		out += line+'\n'
		prev = row
	return out

#######################################

if __name__=="__main__":
	if 1:
		for x in decode(data):
			print(x)
		print('-'*20)
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
			xxx
			xxx
			xxx
			xxx
			xxx
			xxx
			xxx
			xxx
			cos
			cos
			cos
			x TODO jak tego nie bedzie to nie zadziala cos*3
		""".split('\n') if x.strip()])
		print('-'*20)
		print(e)
		print('-'*20)
		for x in decode(e):
			print(x)
