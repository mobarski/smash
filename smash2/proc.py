import os
import sys
import zipfile

# TODO mozliwosc wskazania konkretnego pliku/katalogu z procedurami w name
# TODO default paths - smash proc dir, local dir, local proc dir, zip files?

paths = ['./proc']

def get(name):
	n = name+'.smash'
	for p in paths:
		if p.endswith('.zip'):
			z=zipfile.ZipFile(p)
			if n in z.namelist():
				return z.open(n).read()
		else:
			if n in os.listdir(p):
				fp = os.path.join(p,n)
				return open(fp,'r').read()

if __name__=="__main__":
	print(get('hive'))
