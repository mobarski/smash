from bottle import route, run, template, static_file, request, auth_basic, redirect

def dynamic(tmpl,*args,**kwargs):
	with open('dynamic/'+tmpl+'.html','r') as f:
		raw = f.read()
	return template(raw,*args,**kwargs)

@route('/concept')
def concept3():
	return dynamic('dotarg')

@route('/concept',method='POST')
def concept3():
	import re
	f = request.forms
	#print(str(list(f.allitems())))
	action=f.get('action','show')
	direction=f.get('dir','LR')
	cluster=f.get('cluster','yes')=='yes'
	style=f.get('style','white')
	value=f.get('value','cluster')
	hint=f.get('hint','')
	info=f.get('info','')
	link=f.get('link','')
	filter_type=f.get('filter','omit')
	filter_clusters=[v for k,v in f.items() if k.startswith('cluster_')]
	notation=f.get('notation','')
	question=f.get('question','')
	reverse_clusters=[v for k,v in f.items() if k.startswith('reverse_')]
	rank=f.get('rank','')
	model=f.get('model','')
	area=f.get('area','')
	#print(locals()) # XXX
	dotgen.reload()
	dotgen.generate('tmp/x.dot',direction=direction,cluster=cluster,style=style,value=value,hint=hint,info=info,filter_type=filter_type,filter_clusters=filter_clusters,link=link,notation=notation,question=question,reverse_clusters=reverse_clusters,rank=rank,model=model,area=area)
	if action=="show":
		dot.render('tmp/x.dot','tmp/x','svg')
		bf = open('tmp/x.svg','r')
		b = bf.read()
		bf.close()
		fit = f.get('fit','auto')
		b=re.sub('<title>[^<]*</title>','<title></title>',b)
		if fit=='auto': b=re.sub('<svg width="([^"]+?)" height="([^"]+?)"',r'<svg width="100%" height="90%"',b)
		if fit=='width': b=re.sub('<svg width="([^"]+?)" height="([^"]+?)"',r'<svg width="100%" height="\2"',b)
		if fit=='height': b=re.sub('<svg width="([^"]+?)" height="([^"]+?)"',r'<svg width="\1" height="90%"',b)
		if fit=='no': b=re.sub('<svg width="([^"]+?)" height="([^"]+?)"',r'<svg ',b)
		return b
	else:
		dot.render('tmp/x.dot','tmp/x','pdf')
		redirect("tmp/x.pdf")

run(host='0.0.0.0', port=9090, debug=True) # public