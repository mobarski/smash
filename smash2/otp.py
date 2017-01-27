import os
import sys
import struct
import random
import base64
import array

"""
OneTimePad-Like encoding / decoding
"""

# TODO turn into object
# TODO optimize

__encode = base64.b32encode
__decode = base64.b32decode

def get_pad_path():
	d=os.environ.get('appdata','') or os.environ.get('HOME','') or '.'
	return os.path.join(d,".otp-secret.bin")

def get_pad():
	pad_path = get_pad_path()
	try:
		f = open(pad_path,'rb')
	except:
		init()
		f = open(pad_path,'rb')
	raw = f.read()
	if sys.version_info[0]==2:
		a = array.array('B')
		a.fromstring(raw)
		return a
	else:
		return array.array('B',raw)

def xor_with_pad(text,seed=None):
	if sys.version_info[0]==3 and type(text)==str:
		text=text.encode()
	pad=get_pad()
	if sys.version_info[0]==3:
		random.seed(seed,version=1)
	else:
		random.seed(seed)
	random.shuffle(pad)
	t = array.array('B',text)
	return [a^b for a,b in zip(t,pad)]

def init(length=4096):
	p = os.urandom(length)
	f = open(get_pad_path(),'wb')
	f.write(p)
	# TODO make file private

def encode(s):
	raw_seed=os.urandom(4)
	seed=struct.unpack('I',raw_seed)
	n=xor_with_pad(s,seed)
	b = raw_seed+struct.pack(len(n)*'B',*n)
	text = __encode(b)
	text = text.decode() if sys.version_info[0]==3 else text
	return text.replace('=','x')

def decode(s):
	b = __decode(s.replace('x','=').encode())
	raw_seed,b = b[:4],b[4:]
	seed=struct.unpack('I',raw_seed)
	n = struct.unpack(len(b)*'B',b)
	x = xor_with_pad(n,seed)
	text = struct.pack(len(x)*'B',*x)
	return text.decode() if sys.version_info[0]==3 else text
	
if __name__=="__main__":
	if 0:
		print(xor_with_pad('test'))
	if 1:
		for a in ('test','takt','zzz'):
			b=encode(a)
			c=decode(b)
			print(a,b,c,a==c)
	if 0:
		a=b"test"
		b=b"\xff\x00\xf0\x0f"
		aa=array.array('B',a)
		ba=array.array('B',b)
		print([a^b for a,b in zip(aa,ba)])
