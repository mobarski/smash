# SIMPLE PYTHON-BASED STACK LANGUAGE FOR TEXT MANIPULATION
import re
import itertools
import random
import bisect
import heapq

WORDQUOTE = "'"

def as_int(s):
	try: return int(s)
	except ValueError: return None

def fun_substr(s,a,b):
	if a==0: a=1
	if a>0: a-=1
	if a<0 and b>=-a or b<0: b=None
	else: b=a+b
	return s[a:b]

def stack_eval(code,data=[],env={}):
	quote_mode = False 
	
	if hasattr(data,'lower'):
		stack = [data]
	else:
		stack = data
	print(stack)
	s = stack

	tokens = re.split('\s+',code.strip())
	while tokens:
		op = tokens.pop(0) # TODO if tokens[0] is iter then pop from that iter
		
		if quote_mode:
			if op==']':	quote_mode=False
			else:			s[-1]+=[op]
			continue
		
		# operators
		v = as_int(op)
		if v!=None:		s+=[v]
		elif op=='mul':		s[-2]=s[-2]*s[-1]; s.pop()
		elif op=='div':		s[-2]=s[-2]/s[-1]; s.pop()
		elif op=='add':		s[-2]=s[-2]+s[-1]; s.pop()
		elif op=='sub':		s[-2]=s[-2]-s[-1]; s.pop()
		elif op=='pow':		s[-2]=s[-2]**s[-1]; s.pop()
		elif op=='mod':		s[-2]=s[-2]%s[-1]; s.pop()
		elif op=='lshift':	s[-2]=s[-2]<<s[-1]; s.pop()
		elif op=='rshift':	s[-2]=s[-2]>>s[-1]; s.pop()
		elif op=='and':		s[-2]=s[-2]&s[-1]; s.pop()
		elif op=='or':		s[-2]=s[-2]|s[-1]; s.pop()
		elif op=='xor':		s[-2]=s[-2]^s[-1]; s.pop()
		elif op=='eq':		s[-2]=s[-2]==s[-1]; s.pop()
		elif op=='ne':		s[-2]=s[-2]!=s[-1]; s.pop()
		elif op=='le':		s[-2]=s[-2]<=s[-1]; s.pop()
		elif op=='ge':		s[-2]=s[-2]>=s[-1]; s.pop()
		elif op=='lt':		s[-2]=s[-2]<s[-1]; s.pop()
		elif op=='gt':		s[-2]=s[-2]>s[-1]; s.pop()
		elif op=='neg':		s[-1]=-s[-1]
		elif op=='inv':		s[-1]=~s[-1]
		elif op=='abs':		s[-1]=abs(s[-1])
		elif op=='bool':	s[-1]=bool(s[-1])
		elif op=='not':		s[-1]=not s[-1]
		
		# string
		elif op=='substr':	s[-3]=fun_substr(s[-3],s[-2],s[-1]); s.pop(); s.pop()
		elif op=='strip':	s[-1]=s[-1].strip()
		elif op=='lstrip':	s[-1]=s[-1].lstrip()
		elif op=='rstrip':	s[-1]=s[-1].rstrip()
		elif op=='upper':	s[-1]=s[-1].upper()
		elif op=='lower':	s[-1]=s[-1].lower()
		elif op=='len':		s+=[len(s[-1])] # ALT s[-1]=
		elif op=='print':	print(s.pop())
		elif op=='echo':	print(s[-1])
		
		# re
		elif op=='split':	s[-2]=re.split(s[-1],s[-2]); s.pop()
		elif op=='findall':	s[-2]=re.findall(s[-1],s[-2]); s.pop()
		elif op=='finditer':	s[-2]=re.finditer(s[-1],s[-2]); s.pop()
		# TODO search match fullmatch sub subn
		
		# list
		elif op=='slice':	s[-3]=s[-3][s[-2]:s[-1]]; s.pop(); s.pop()
		elif op=='join':	s[-2]=s[-1].join(s[-2]); s.pop()
		elif op=='zip':		s[-2]=zip(s[-2],s[-1]); s.pop() # ALT s[-1],s[-2]
		elif op=='head':	head,rest=s[-1][0],s[-1][1:]; s[-1]=rest; s+=[head]
		elif op=='get':		s[-1]=s[-2][s[-1]] # ALT s[-2]= # TODO different name AT INDEX KEY TH NTH
		
		# iter
		#elif op=='tee':			s[-2]=itertools.tee(s[-2],s[-1]); s.pop()
		elif op=='repeat':		s[-2]=itertools.repeat(s[-2],s[-1]); s.pop()
		elif op=='chain':		s[-1]=itertools.chain.from_iterable(s[-1])
		elif op=='product':		s[-2]=itertools.product(s[-2],repeat=s[-1]); s.pop()
		elif op=='permutations':	s[-2]=itertools.permutations(s[-2],r=s[-1]); s.pop()
		elif op=='combinations':	s[-2]=itertools.combinations(s[-2],r=s[-1]); s.pop()
		
		# types
		elif op=='list':	s[-1]=list(s[-1])
		elif op=='set':		s[-1]=set(s[-1])
		elif op=='str':		s[-1]=str(s[-1])
		elif op=='tuple':	s[-1]=tuple(s[-1])
		
		# random
		elif op=='randint':	s[-2]=random.randint(s[-2],s[-1]); s.pop()
		elif op=='sample':	s[-2]=random.sample(s[-2],s[-1]); s.pop()
		elif op=='choice':	s[-1]=random.choice(s[-1])
		elif op=='shuffle':	random.shuffle(s[-1])
		elif op=='random':	s+=[random.random()]
		
		# bisect
		elif op=='insort_left':	bisect.insort_left(s[-2],s[-1]); s.pop()
		elif op=='insort_right':	bisect.insort_right(s[-2],s[-1]); s.pop()
		elif op=='insort':		bisect.insort(s[-2],s[-1]); s.pop()
		elif op=='bisect_left':	s[-2]=bisect.bisect_left(s[-2],s[-1]); s.pop()
		elif op=='bisect_right':	s[-2]=bisect.bisect_right(s[-2],s[-1]); s.pop()
		elif op=='bisect':		s[-2]=bisect.bisect(s[-2],s[-1]); s.pop()
		
		# heapq
		elif op=='heapify':		heapq.heapify(s[-1])
		elif op=='heappush':		heapq.heappush(s[-2],s[-1]); s.pop()
		elif op=='heappushpop':	s[-2]=heapq.heappushpop(s[-2],s[-1]); s.pop()
		elif op=='nlargest':		s[-2]=heapq.nlargest(s[-1],s[-2]); s.pop()
		elif op=='nsmallest':	s[-2]=heapq.nsmallest(s[-1],s[-2]); s.pop()
		elif op=='heappop':		s[-1]=heapq.heappop(s[-1])
		#elif op=='merge':		s[-1]=heapq.merge(s[-1])
		
		
		# stack language
		elif op=='[':		s+=[list()]; quote_mode=True
		elif op=='swap':	s[-2],s[-1]=s[-1],s[-2]
		elif op=='dup':		s+=[s[-1]]
		elif op=='drop':	s.pop()
		elif op=='drop2':	s.pop(); s.pop()
		elif op=='over':	s+=[s[-2]]
		elif op=='defer':	s+=[tokens.pop(0)] # TODO remove?
		elif op=='run':		tokens[0:0]=s.pop()
		elif op=='store':	env[s[-1]]=s[-2]; s.pop();s.pop() # TODO different name
		elif op in env:		s+=[env[op]]
		elif op.startswith(WORDQUOTE): s+=[op[len(WORDQUOTE):]]
		else:				s+=[op]
	print(stack,env)

def_env = {'white':'\s+', 'comma':',', 'space':' ', 'empty':'', 'none':None, 'true':True, 'false':False}
stack_eval('abc 2 combinations list','block\tof  data', env=def_env)

"""
[ 1 2 3 4 5 6 ] map

"""