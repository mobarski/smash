from collections import namedtuple, defaultdict
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
	if value=='cluster2':
		v = h(n.cluster2 or n.cluster or n.node,lo,hi,0)
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
	#if link=='src': return '/tabs/{0}'.format(n.src) if n.src else ''
	if link=='src': return '/tab/{0}.{1}'.format(n.src_db,n.src) if n.src and n.src_db else ''
	if link=='bg': return '/term/{0}'.format(n.bg) if n.bg else ''

# TODO
def get_edge_style(edge,notation):
	rel = edge.relation
	rel2 = edge.relation2
	out = ""
	#if 'short' in edge.tags: out += " weight=100"
	#if 'question' in edge.tags: out += " weight=5"
	if 'long' in edge.tags: out += " weight=0"
	if "x" in rel: return out
	if not notation: return out
	if notation=='simple':
		if "o" in rel: out += " style=dashed"
		return out
	if notation=='obarski1':
		if "o" in rel: out += " style=dashed"
		if "m" in rel: out += " arrowhead=dot"
		elif "g" in rel: out += " arrowhead=onormal"
		elif "a" in rel: out += " arrowhead=odiamond"
		#else: out += " arrowhead=odot arrowsize=0.5" # XXX 
		if edge.srcfk:
			#out += ' label="{0}"'.format(edge.srcfk) # TODO label vs xlabel
			pass
		# not rel2 support?
		return out
	if notation=='obarski1b':
		if "o" in rel: out += " style=dashed"
		if "m" in rel: out += " arrowtail=odiamond dir=back"
		elif "g" in rel: out += " arrowhead=onormal"
		elif "a" in rel: out += " arrowhead=odiamond"
		return out
	if notation=='obarski1c':
		if "o" in rel: out += " style=dashed"
		if "m" in rel: out += " arrowtail=dot dir=back"
		elif "g" in rel: out += " arrowhead=onormal"
		elif "a" in rel: out += " arrowhead=odiamond"
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
	if notation=='uml2':
		#if "o" in rel: out += " style=dashed"
		if "m" in rel: out += " arrowtail=odiamond dir=back"
		elif "g" in rel: out += " arrowhead=onormal"
		elif "a" in rel: out += " arrowhead=odiamond"
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
	rec_line = ""
	for line in f.readlines():
		rec_line += line
		if rec_line.count('"')%2==1:
			continue
		r = [x.strip() for x in re.split(dlm,rec_line)]
		out += [record(*r)]
		rec_line = ""
	return out

def node_inheritance():
	for n in nodes.values():
		if n.model=='conceptual': continue
		parent_k = ('conceptual',n.area,n.node)
		if parent_k not in nodes: continue
		parent = nodes[parent_k]
		if not n.cluster: n=n._replace(cluster=parent.cluster)
		if not n.cluster2: n=n._replace(cluster2=parent.cluster2)
		if not n.label: n=n._replace(label=parent.label)
		if not n.tags: n=n._replace(tags=parent.tags)
		if not n.rank: n=n._replace(rank=parent.rank)
		if not n.count: n=n._replace(count=parent.count)
		if not n.src: n=n._replace(src=parent.src)
		if not n.src_db: n=n._replace(src_db=parent.src_db)
		if not n.src_col: n=n._replace(src_col=parent.src_col)
		if not n.bg: n=n._replace(bg=parent.bg)
		k = (n.model,n.area,n.node)
		nodes[k] = n

def reload():
	global nodes
	global edges
	node_list = load('data/conceptual-n.xls',"model area cluster cluster2 node label tags rank count src src_db src_col bg",rec='v')
	edges = load('data/conceptual-e.xls',"model area node node2 tags relation relation2 srcfk srcfk2",rec='e')
	nodes = {}
	for n in node_list:
		k = (n.model, n.area, n.node)
		nodes[k] = n
	node_inheritance()
reload()

# TODO rename style to colors
def generate(filename, cluster=True, direction='TD', style='', value='', hint='', info='', filter_type='omit', filter_clusters=[],link='',notation='',question='',reverse_clusters=[],rank='',model='',area=''):
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
	ranked = defaultdict(set)
	cluster_by_node = defaultdict(str)
	reversed_edges= defaultdict(set)
	prev_cluster=''
	for n in nodes.values():
		if n.model != model: continue
		if n.area != area: continue
		cluster_by_node[n.node] = n.cluster
		if question=='no' and 'question' in n.tags: continue
		if filter_type=='omit' and n.cluster and n.cluster in filter_clusters: continue
		#if filter_type=='omit' and not n.cluster and n.node in filter_clusters: continue
		if filter_type=='select' and n.cluster and n.cluster not in filter_clusters: continue
		#if n.cluster in reverse_clusters: reversed_nodes.add(n.node)
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
		aux += ' href="{0}" target="_top"'.format(href) if href else ''
		print(' %s [label="%s" %s]'%(n.node,label,aux))
		if n.rank:
			ranked[n.rank].add(n.node)
	if prev_cluster != '' and cluster: print('}\n')
	print('\n')

	# edges
	for e in edges:
		if e.model != model: continue
		if e.area != area: continue
		if (e.node in visible_nodes and e.node2 in visible_nodes) or 'question' in e.tags:
			s = get_edge_style(e,notation)
			e_style = '[{0}]'.format(s) if s else ''
			if 'question' in e.tags and question=='no' and e.node2 in visible_nodes:
				print('fact -> %s %s'%(e.node2,e_style))
			elif (e.node in visible_nodes and e.node2 in visible_nodes):
				#print('%s -> %s %s'%(e.node,e.node2,e_style))
				if cluster_by_node[e.node] in reverse_clusters or e.node in reverse_clusters or e.node2 in reverse_clusters:
					print('%s -> %s %s'%(e.node2,e.node,e_style),file=sys.stderr)
					print('%s -> %s %s'%(e.node2,e.node,e_style)) # TODO style
				else:
					print('%s -> %s %s'%(e.node,e.node2,e_style))

	# TODO vs reverse
	if rank=='force':
		for r,n_list in ranked.items():
			print('{rank=same; '+';'.join(n_list)+'}')

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

