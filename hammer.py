# SIMPLE PYTHON-BASED STACK LANGUAGE FOR TEXT MANIPULATION
import re
import itertools
import random
import bisect
import heapq
import time
import sys
import array
import math
import pprint

WORDQUOTE = "'"

def as_int(s):
	try: return int(s)
	except: return None

def fun_substr(s,a,b):
	if a==0: a=1
	if a>0: a-=1
	if a<0 and b>=-a or b<0: b=None
	else: b=a+b
	return s[a:b]

def stack_eval(code,stack=[],env={}):
	quote_mode = False 
	s = stack

	tokens = re.split('\s+',code.strip()) # TODO quotes
	while tokens:
		if hasattr(tokens[0],'next') or hasattr(tokens[0],'__next__'): 
			try:
				op = next(tokens[0])
			except StopIteration:
				tokens.pop(0)
				continue
		else:
			op = tokens.pop(0)
		
		if quote_mode:
			if op==']':	quote_mode=False
			else:			s[-1]+=[op]
			continue
		
		# TODO change into dict[op] -> fun
		
		# operators
		v = as_int(op)
		if v!=None:		s+=[v]
		elif op=='mul':		s[-2]=s[-2]*s[-1]; s.pop()
		elif op=='div':		s[-2]=s[-2]/s[-1]; s.pop()
		elif op=='add':		s[-2]=s[-2]+s[-1]; s.pop()
		elif op=='sub':		s[-2]=s[-2]-s[-1]; s.pop()
		elif op=='pow':		s[-2]=s[-2]**s[-1]; s.pop()
		elif op=='mod':		s[-2]=s[-2]%s[-1]; s.pop()
		elif op=='divmod':	s[-2],s[-1]=divmod(s[-2],s[-1])
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
		
		# string / seq
		elif op=='substr':	s[-3]=fun_substr(s[-3],s[-2],s[-1]); s.pop(); s.pop()
		elif op=='replace':	s[-3]=s[-3].replace(s[-2],s[-1]); s.pop(); s.pop() # TODO kolejnosc?
		elif op=='ljust':	s[-2]=s[-2].ljust(s[-1]); s.pop();
		elif op=='rjust':	s[-2]=s[-2].rjust(s[-1]); s.pop();
		elif op=='center':	s[-2]=s[-2].center(s[-1]); s.pop();
		elif op=='strip':	s[-1]=s[-1].strip()
		elif op=='lstrip':	s[-1]=s[-1].lstrip()
		elif op=='rstrip':	s[-1]=s[-1].rstrip()
		elif op=='upper':	s[-1]=s[-1].upper()
		elif op=='lower':	s[-1]=s[-1].lower()
		elif op=='len':		s+=[len(s[-1])] # ALT s[-1]=
		elif op=='print':	print(s.pop())
		elif op=='pprint':	pprint.pprint(s.pop())
		elif op=='echo':	print(s[-1])
		elif op=='min':		s[-1]=min(s[-1])
		elif op=='max':		s[-1]=max(s[-1])
		elif op=='min2':	s[-2]=min(s[-2],s[-1]); s.pop()
		elif op=='max2':	s[-2]=max(s[-2],s[-1]); s.pop()
		
		# re
		elif op=='split':	s[-2]=re.split(s[-1],s[-2]); s.pop()
		elif op=='findall':	s[-2]=re.findall(s[-1],s[-2]); s.pop()
		elif op=='finditer':	s[-2]=re.finditer(s[-1],s[-2]); s.pop()
		# TODO search match fullmatch sub subn
		
		# textwrap
		elif op=='wrap':	s[-2]=textwrap.wrap(s[-2],s[-1]); s.pop()
		elif op=='fill':	s[-2]=textwrap.fill(s[-2],s[-1]); s.pop()
		elif op=='dedent':	s[-1]=textwrap.dedent(s[-1])
		elif op=='indent':	s[-2]=textwrap.indent(s[-2],s[-1]); s.pop()
		
		# list
		elif op=='slice':	s[-3]=s[-3][s[-2]:s[-1]]; s.pop(); s.pop()
		elif op=='join':	s[-2]=s[-1].join(s[-2]); s.pop()
		elif op=='append':	s[-2].append(s[-1]); s.pop()
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
		elif op=='range':		s[-1]=range(s[-1])
		elif op=='range2':		s[-2]=range(s[-2],s[-1]); s.pop()
		elif op=='range3':		s[-3]=range(s[-3],s[-2],s[-1]); s.pop();s.pop()
		
		# types
		elif op=='list':	s[-1]=list(s[-1])
		elif op=='set':		s[-1]=set(s[-1])
		elif op=='str':		s[-1]=str(s[-1])
		elif op=='tuple':	s[-1]=tuple(s[-1])
		elif op=='float':	s[-1]=float(s[-1])
		elif op=='int':		s[-1]=int(s[-1])
		elif op=='iter':	s[-1]=iter(s[-1])
		elif op=='nlist':	n=s.pop(); s[-n]=s[-n:]; del s[-n+1:]
		
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
		
		# time
		elif op=='time':		s+=[time.time()]
		elif op=='clock':		s+=[time.clock()]
		elif op=='sleep':		time.sleep(s[-1]); s.pop()
		
		# TODO struct
		# TODO array
		# TODO pickle
		# TODO if def
		
		elif op=='map':		a,b=s[-2:]; s[-2]=[]; s.pop(); tokens.insert(0,itertools.chain.from_iterable(map(lambda x:itertools.chain([x],b,['append']),a)));
		elif op=='reduce':	a,b=s[-2:]; s[-2]=itertools.chain.from_iterable(map(lambda x:itertools.chain([x],b),a)); s.pop()
		#elif op=='reduce':	tokens[0:0]=['unrot','map']
		
		# sys
		elif op=='exit':	sys.exit(s[-1])
		elif op=='argv':	s+=[sys.argv]
		
		# math
		elif op=='pi':		s+=[math.pi]
		elif op=='e':		s+=[math.e]
		elif op=='ceil':	s[-1]=math.ceil(s[-1])
		elif op=='floor':	s[-1]=math.floor(s[-1])
		elif op=='exp':		s[-1]=math.exp(s[-1])
		elif op=='fabs':	s[-1]=math.fabs(s[-1])
		elif op=='fsum':	s[-1]=math.fsum(s[-1])
		elif op=='degrees':	s[-1]=math.degrees(s[-1])
		elif op=='radians':	s[-1]=math.radians(s[-1])
		elif op=='atan2':	s[-2]=math.atan2(s[-2],s[-1]); s.pop()
		elif op=='log':		s[-2]=math.log(s[-2],s[-1]); s.pop()
		elif op=='sin':		s[-1]=math.sin(s[-1])
		elif op=='cos':		s[-1]=math.cos(s[-1])
		elif op=='tan':		s[-1]=math.tan(s[-1])
		elif op=='asin':	s[-1]=math.asin(s[-1])
		elif op=='acos':	s[-1]=math.acos(s[-1])
		elif op=='atan':	s[-1]=math.atan(s[-1])
		
		# array
		#elif op=='array':	s[-2]=array.array(s[-1],s[-2]); s.pop()
		
		# other
		#elif op=='input':	s[-1]=input(s[-1])
		elif op=='repr':	s[-1]=repr(s[-1])
		
		# stack language
		elif op.startswith(WORDQUOTE): s+=[op[len(WORDQUOTE):]]
		elif op=='[':		s+=[list()]; quote_mode=True
		elif op=='depth':	s+=[len(s)]
		elif op=='swap':	s[-2],s[-1]=s[-1],s[-2]
		elif op=='rot':		s[-3],s[-2],s[-1]=s[-2],s[-1],s[-3]
		elif op=='unrot':	s[-3],s[-2],s[-1]=s[-1],s[-3],s[-2]
		elif op=='dup':		s+=[s[-1]]
		elif op=='drop':	s.pop()
		elif op=='drop2':	s.pop(); s.pop()
		elif op=='over':	s+=[s[-2]]
		elif op=='pick':	s[-1]=s[-s[-1]-1]
		elif op=='nip':		s[-2]=s[-1]; s.pop()
		elif op=='defer':	s+=[tokens.pop(0)] # TODO remove?
		elif op=='run':		tokens.insert(0,iter(s.pop()))
		elif op=='store':	env[s[-1]]=s[-2]; s.pop();s.pop() # TODO different name
		elif op=='stack':	s+=[s] # ALT s.copy()
		elif op=='curry':	s[-2]=[s[-2]]+s[-1]; s.pop() # TODO rename
		elif op in env:		s+=[env[op]]
		else:				s+=[op]
	return stack
	
env = {}
env['white']='\s+'
env['comma']=','
env['dot']='.'
env['space']=' '
env['empty']=''
env['none']=None
env['true']=True
env['false']=False
env['nan']=float('nan')
env['inf']=float('inf')

code = """
[ 1 2 3 4 5 ] 0 swap [ 2 pow add ] reduce list print
"""
stack_eval(code, env=env)
