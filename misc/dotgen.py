from collections import namedtuple
from copy import copy
import sys
import re

###  XXX ##########################################
from random import randint
from binascii import crc32
def h(s,lo,hi,offset=0):
	return lo+((crc32(s.encode())+offset)%(hi-lo+1))

import math
def scale(x,base=10,lo=1,hi=None,div=None):
	if div: x/=div
	if x<base: return lo
	if base==10: val=math.log10(x)
	else:
		val=math.log(x,base)
	val += lo
	if hi and val>hi: return hi
	return int(val)
	
def progress(x,n=5,black="&#9679;",white="&#9675;"):
	if x<0: x=0
	if type(x)==float: x=int(n*x)
	if x>n: x=n
	return black*x+white*(n-x)

def rsplit(text,delimiters):
	"recursive split"
	d = delimiters[0]
	s = text.split(d)
	if len(delimiters)==1:
		return s if len(s)>1 else s[0]
	else:
		x = [rsplit(x,delimiters[1:]) for x in s]
		return x if len(x)>1 else x[0]
#################################################
def get_color(node,value,scheme,lo,hi):
	n = node
	if lo<hi: reverse=False
	else:
		reverse=True
		lo,hi=hi,lo
	if not value or value=='cluster':
		v = h(n.cluster or n.node,lo,hi,0)
	if value=='count':
		v = n.count
		if v=='': return ""
		v = scale(int(v),lo=lo,hi=hi)
	if value=='bg':
		v = n.bg
		if v=='': return ""
		v = lo
	if value=='src':
		v = n.src
		if v=='': return ""
		v = lo
	if value=='prog':
		v = (1 if n.bg else 0) + (1 if n.src else 0) + (1 if n.count else 0)
		if v==0: return "white"
		v = lo+int((v/3)*(hi-lo))
	if reverse: v=hi-(v-lo)
	return "/{0}/{1}".format(scheme,v)

def get_tooltip(node,hint):
	n = node
	if hint=='count': return n.count
	if hint=='src': return n.src
	if hint=='bg': return n.bg
	return n.node

def get_label(node,info,direction):
	n = node
	label = n.label or n.node.replace('_',' ')
	if not info: return label
	if info=='count': out = '{0}|{1}'.format(label,n.count) if n.count else label
	if info=='src': out = '{0}|{1}'.format(label,n.src) if n.src else label
	if info=='bg': out = '{0}|{1}'.format(label,n.bg) if n.bg else label
	if info=='prog':
		v = (1 if n.bg else 0) + (1 if n.src else 0) + (1 if n.count else 0)
		out = '{0}|{1} / 3'.format(label,v) if v else label
	return '{'+out+'}' if direction.upper()=='TD' and '|' in out else out

def get_href(node,link):
	n = node
	if not link: return ''
	if link=='src': return '/tabs/{0}'.format(n.src) if n.src else ''

# TODO
def get_edge_style(edge,notation):
	if not notation: return ''
	rel = edge.relation
	rel2 = edge.relation2
	if "x" in rel: return ''
	out = ""
	if notation=='obarski':
		if "o" in rel: out += " style=dashed"
		if "m" in rel: out += " arrowhead=dot"
		elif "g" in rel: out += " arrowhead=onormal"
		elif "a" in rel: out += " arrowhead=odiamond"
		else: out += " arrowhead=odot arrowsize=0.5" # XXX 
		if edge.srcfk:
			#out += ' label="{0}"'.format(edge.srcfk) # TODO label vs xlabel
			pass
		# not rel2 support?
		return out
	if notation=='obarski2':
		if "o" in rel and "m" not in rel: out += " arrowhead=odot"
		if "o" in rel and "m" in rel: out += " arrowhead=dotodot"
		if "m" in rel and "o" not in rel: out += " arrowhead=dot"
		if "g" in rel: out += " arrowhead=onormal"
		if "a" in rel: out += " arrowhead=odiamond"
		if rel2: out += " dir=both"
		if "o" in rel2 and "m" not in rel2: out += " arrowtail=odot"
		if "o" in rel2 and "m" in rel2: out += " arrowtail=dotodot"
		if "m" in rel2 and "o" not in rel2: out += " arrowtail=dot"
		if "g" in rel2: out += " arrowtail=onormal"
		if "a" in rel2: out += " arrowtail=odiamond"		
		return out
	if notation=='omt':
		if "o" in rel: return "arrowhead=odot"
		if "m" in rel: return "arrowhead=dot"
		if "g" in rel: return "arrowhead=onormal"
		if "a" in rel: return "arrowhead=odiamond"
		# not rel2 support?
		return ''
	if notation=='express':
		if "o" in rel: out +=  " style=dashed"
		if "g" in rel: out +=  " style=bold"
		out += ' arrowhead=odot'
		return out
	if notation=='crow': # martin / IE notation
		if "o" in rel and "m" in rel: out += " arrowhead=crowodot"
		if "o" in rel and "m" not in rel: out += " arrowhead=teeodot"
		if "o" not in rel and "m" in rel: out += " arrowhead=crowtee"
		#if "o" not in rel and "m" not in rel: out += " arrowhead=teetee" # optional
		if "g" in rel: out += " arrowhead=onormal" # ???
		if "a" in rel: out += " arrowhead=odiamond" # ???
		if rel2: out += " dir=both"
		if "o" in rel2 and "m" in rel2: out += " arrowtail=crowodot"
		if "o" in rel2 and "m" not in rel2: out += " arrowtail=teeodot"
		if "o" not in rel2 and "m" in rel2: out += " arrowtail=crowtee"
		#if "o" not in rel2 and "m" not in rel2: out += " arrowtail=teetee" # optional
		if "g" in rel2: out += " arrowtail=onormal" # ???
		if "a" in rel2: out += " arrowtail=odiamond" # ???		
		return out
	if notation=='uml':
		if "o" in rel and "m" in rel: out += ' headlabel="0..N"'
		if "o" in rel and "m" not in rel: out += ' headlabel="0..1"'
		if "o" not in rel and "m" in rel: out += ' headlabel="1..N"'
		if "o" not in rel and "m" not in rel: out += ' headlabel=""' # optional
		if "g" in rel: out += " arrowhead=onormal"
		if "a" in rel: out += " arrowhead=odiamond"
		if "o" in rel2 and "m" in rel2: out += ' taillabel="0..N"'
		if "o" in rel2 and "m" not in rel2: out += ' taillabel="0..1"'
		if "o" not in rel2 and "m" in rel2: out += ' taillabel="1..N"'
		if "o" not in rel2 and "m" not in rel2: out += ' taillabel=""' # optional
		if "g" in rel2: out += " arrowtail=onormal"
		if "a" in rel2: out += " arrowtail=odiamond"	
		return out
	
#################################################

# ALT:
# 1 - m-mandatory/r-required o-optional
# 2 - s-single m-multiple
# 3 - g-generalization a-aggregation

# TODO - N - entity / attribute / attribute_set(denormalization)

# TODO - GNE - GLOBALS

#################################################

# data source

def load(filename, columns, skip_header=True, dlm='\t', rec='rec'):
	record = namedtuple(rec,columns)
	f = open(filename,'r')
	if skip_header: f.readline()
	out = []
	for line in f.readlines():
		r = [x.strip() for x in re.split(dlm,line)]
		out += [record(*r)]
	return out

nodes = load('data/conceptual-n.xls',"area graph cluster cluster2 node label tags count src bg",rec='v')
edges = load('data/conceptual-e.xls',"area graph node node2 tags relation relation2 srcfk",rec='e')

# TODO rename style to colors
def generate(filename, cluster=True, direction='TD', style='', value='', hint='', info='', filter_type='omit', filter_clusters=[],link='',notation='',question=''):
	# generator
	sys.stdout=open(filename,'w')
	print('strict digraph {')
	print('graph [rankdir={0} compound=true]'.format(direction))
	print('edge [arrowhead=none]')
	print('node [shape=record style="rounded,filled" fillcolor=white]')
	print('')

	if style:
		color_scheme = style.split(':')[0]
		color_lo = int(style.split(':')[1])
		color_hi = int(style.split(':')[2])

	# nodes
	visible_nodes = set()
	prev_cluster=''
	for n in nodes:
		if question=='no' and 'question' in n.tags: continue
		if filter_type=='omit' and n.cluster and n.cluster in filter_clusters: continue
		#if filter_type=='omit' and not n.cluster and n.node in filter_clusters: continue
		if filter_type=='select' and n.cluster and n.cluster not in filter_clusters: continue
		visible_nodes.add(n.node)
		#label = n.label or n.node.replace('_',' ')
		label = get_label(n,info,direction)
		if prev_cluster != n.cluster and cluster:
			if prev_cluster	!= '': print('}\n')
			if n.cluster	!= '': print('\nsubgraph cluster_%s { graph[style=dotted]'%(n.cluster))
		prev_cluster=n.cluster
		aux = ''
		if 'question' in n.tags: aux+=' shape=circle'
		if 'fact' in n.tags: aux+=' width=2 fontsize=28'
		if style:
			color = get_color(n,value,color_scheme,color_lo,color_hi)
			aux+=' fillcolor="{0}"'.format(color)
		tooltip = get_tooltip(n,hint)
		aux+=' tooltip="{0}"'.format(tooltip)
		href = get_href(n,link)
		aux += ' href="{0}"'.format(href) if href else ''
		print(' %s [label="%s" %s]'%(n.node,label,aux))
	if prev_cluster != '' and cluster: print('}\n')
	print('\n')

	# edges
	for e in edges:
		if (e.node in visible_nodes and e.node2 in visible_nodes) or 'question' in e.tags:
			e_style = ''
			if notation:
				s = get_edge_style(e,notation)
				if s:
					e_style = '[{0}]'.format(s)
			if 'question' in e.tags and question=='no' and e.node2 in visible_nodes:
				print('fact -> %s %s'%(e.node2,e_style))
			elif (e.node in visible_nodes and e.node2 in visible_nodes):
				print('%s -> %s %s'%(e.node,e.node2,e_style))

	print('}')
	sys.stdout=sys.__stdout__

### XXX #########################
import subprocess
def render(dot, out, fmt='png'):
	f = open(dot,'r') if type(dot)==str else dot
	cmd = "C:\\graphviz\\bin\\dot.exe"
	rc=subprocess.call("{2} -T{1} -o{0}.{1}".format(out,fmt,cmd),stdin=f,shell=True)
	f.close() if type(dot)==str else 0
	return rc
###############################

if __name__=="__main__":
	#generate('test.dot')
	render('test.dot','test')
	#print(progress(0.99,3))
	#print(rsplit('a,1:b,2|z','|,:.'))
	
