from functools import partial

# simple function composition mechanism
def pipe(out,*args):
	for fun in args:
		if callable(fun):
			out = fun(out)
		else: print(out,fun) # TODO partial?
	return out


def sort_by(key=None, reverse=False): return partial(sorted,key=key,reverse=reverse)
def filter_by(key=None): return partial(filter,key)

if __name__=="__main__":
	pipe(
		[4,0,1,2],
		filter_by(lambda x:x>=2),
		list,
		print
	)

