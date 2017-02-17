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
#################################################

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
		r = [x.strip() for x in re.split(dlm,line)]
		out += [record(*r)]
	return out

nodes = load('data/conceptual-n.xls',"area graph cluster node label tags",rec='v')
edges = load('data/conceptual-e.xls',"area graph cluster node node2 tags",rec='e',lst='node2')

# TODO rename style to colors
def generate(filename, cluster=True, direction='TD', style=''):
	# generator
	sys.stdout=open(filename,'w')
	print('strict digraph {')
	print('graph [rankdir={0} compound=true]'.format(direction))
	print('edge [arrowhead=none]')
	print('node [shape=box style="rounded,filled" fillcolor=white]')
	print('')

	if style:
		color_scheme = style.split(':')[0]
		color_lo = int(style.split(':')[1])
		color_hi = int(style.split(':')[2])

	# nodes
	prev_cluster=''
	for n in nodes:
		label = n.label or n.node.replace('_',' ')
		if prev_cluster != n.cluster and cluster:
			if prev_cluster	!= '': print('}\n')
			if n.cluster	!= '': print('\nsubgraph cluster_%s { graph[style=invis]'%(n.cluster))
		prev_cluster=n.cluster
		aux = ''
		if 'question' in n.tags: aux+=' shape=circle'
		if 'fact' in n.tags: aux+=' width=2 fontsize=28'
		if style:
			color_id = h(n.cluster or n.node,color_lo,color_hi,0)
			aux+=' fillcolor="/{0}/{1}"'.format(color_scheme,color_id)
		print(' %s [label="%s" %s]'%(n.node,label,aux))
	if prev_cluster != '' and cluster: print('}\n')
	print('\n')

	# edges
	for e in edges:
		print('%s -> %s'%(e.node,e.node2))

	print('}')
	sys.stdout=sys.__stdout__

### XXX #########################
import subprocess
def render(dotname, outname, fmt='png'):
	f = open(dotname,'r')
	cmd = "C:\\graphviz\\bin\\dot.exe"
	rc=subprocess.call("{2} -T{1} -o{0}.{1}".format(outname,fmt,cmd),stdin=f,shell=True)
	f.close()
	return rc
###############################

if __name__=="__main__":
	generate('test.dot')
