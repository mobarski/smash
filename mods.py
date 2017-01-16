import util
import parse

def should_run(section,frame):
	args = parse.args(section)
	
	# handle overwriting of arguments
	if util.flag(frame.get('force','false')):
		return True
	args += [('skip',frame.get('skip','false'))]
	args += [('run',frame.get('run','true'))]
	args += [('when',frame.get('when','true'))]
	
	for k,v in args:
		if k not in ('skip','run','when'): continue
		v = frame.render(v)
		#print('DEBUG COND',k,v,util.flag(v))
		if k=='skip':
			if util.flag(v):
				return False
		elif k=='run':
			if not util.flag(v):
				return False
		elif k=='when':
			if not v.strip():
				return False
	return True
