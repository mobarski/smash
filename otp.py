import os
import sys
import struct
import random
import base64

"""
OneTimePad-Like encoding / decoding
"""

# TODO optimize

__encode = base64.b32encode
__decode = base64.b32decode

def get_pad_path():
	d=os.environ.get('appdata','') or os.environ.get('HOME','') or '.'
	return os.path.join(d,".otp-secret.bin")

def get_pad(length,seed=0):
	try:
		pad = list(open(get_pad_path(),'rb').read(length))
	except:
		init()
		pad = list(open(get_pad_path(),'rb').read(length))
	random.seed(seed)
	random.shuffle(pad)
	return pad

def xor_with_pad(s,seed=0):
	p=get_pad(len(s),seed)
	if sys.version_info[0]==3 and type(s)==str:
		s=s.encode()
	if sys.version_info[0]==2:
		try:
			x = [(ord(a)^ord(b)) for a,b in zip(s,p)]
		except:
			x = [(a^ord(b)) for a,b in zip(s,p)]
		return x
	else:
		x = [a^b for a,b in zip(s,p)]
		return x

def init(length=4096):
	p = os.urandom(length)
	f = open(get_pad_path(),'wb')
	f.write(p)
	# TODO make file private

def encode(s):
	raw_seed= os.urandom(4)
	seed=struct.unpack('i',raw_seed)
	n=xor_with_pad(s,seed)
	b = raw_seed+struct.pack(len(n)*'B',*n)
	return __encode(b).decode()

def decode(s):
	b = __decode(s.encode())
	raw_seed,b = b[:4],b[4:]
	seed=struct.unpack('i',raw_seed)
	n = struct.unpack(len(b)*'B',b)
	x = xor_with_pad(n,seed)
	return struct.pack(len(x)*'B',*x).decode()

if __name__=="__main__":
	for a in ('test','takt'):
		b=encode(a)
		c=decode(b)
		print(a,b,c)
