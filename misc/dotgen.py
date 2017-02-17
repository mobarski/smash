from collections import namedtuple
from copy import copy
import sys
import re

# XXX
from random import randint
from binascii import crc32
def h(s,lo,hi):
	return lo+(crc32(s.encode())%(hi-lo+1))

# TODO - GNE GLOBALS
# TODO - N SHAPE
# TODO - N STYLE FILLCOLOR
# TODO - N URL
# TODO - E STYLE
# TODO - E DIR
# TODO - E ARROWHEAD
# TODO - E ARROWTAIL
# TODO - C STYLE

# data source

def load(filename, columns, skip_header=True, dlm='\t', rec='rec', lst_dlm='\s+', lst=''):
	record = namedtuple(rec,columns)
	f = open(filename,'r')
	if skip_header: f.readline()
	out = []
	for line in f.readlines():
		r = record(*[x.strip() for x in re.split(dlm,line)])
		if not lst:
			out += [r]
		else:
			for x in re.split(lst_dlm,r._asdict()[lst]):
				r2 = r._replace(**{lst:x})
				out += [record(*r2)]
	return out

nodes = load('conceptual-n.xls',"area graph cluster node label tags",rec='v')
edges = load('conceptual-e.xls',"area graph cluster node node2 tags",rec='e',lst='node2')

# generator

sys.stdout=open('test.dot','w')
print('strict digraph {')
print('graph [rankdir=TD compound=true]')
print('edge [arrowhead=none]')
print('node [shape=box style="rounded,filled" fillcolor=white]')
print('')

# nodes
prev_cluster=''
for n in nodes:
	label = n.label or n.node.replace('_',' ')
	if prev_cluster != n.cluster:
		if prev_cluster	!= '': print('}\n')
		if n.cluster	!= '': print('\nsubgraph cluster_%s { graph[style=invis]'%(n.cluster))
	prev_cluster=n.cluster
	aux = ''
	if 'question' in n.tags: aux+=' shape=circle'
	if 'fact' in n.tags: aux+=' shape=doublecircle'
	#aux+=' fillcolor="/pastel28/{0}"'.format(randint(1,8)) # XXX
	aux+=' fillcolor="/pastel28/{0}"'.format(h(label,1,8)) # XXX
	print(' %s [label="%s" %s]'%(n.node,label,aux))
if prev_cluster != '': print('}\n')
print('\n')

# edges
for e in edges:
	print('%s -> %s'%(e.node,e.node2))

print('}')
