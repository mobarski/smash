"""
xor pad encoding / decoding

>>> decode(encode("secret"))
'secret'
"""

import os
import sys
import struct
import random
import base64
import array

# TODO turn into object
# TODO optimize
# TODO ochrona przed uzyciem podkladki znanego hasla

__encode = base64.b32encode
__decode = base64.b32decode

def _get_pad_path():
	d=os.environ.get('appdata','') or os.environ.get('HOME','') or '.'
	return os.path.join(d,".otp-secret.bin")

def _get_pad():
	"get pad as array of unsigned bytes"
	pad_path = _get_pad_path()
	try:
		f = open(pad_path,'rb')
	except:
		_init()
		f = open(pad_path,'rb')
	raw = f.read()
	if sys.version_info[0]==2:
		a = array.array('B')
		a.fromstring(raw)
		return a
	else:
		return array.array('B',raw)

def _xor_with_pad(text,seed=None):
	"xor text with pseudo-randomly shuffled pad"
	if sys.version_info[0]==3 and type(text)==str:
		text=text.encode()
	pad=_get_pad()
	if sys.version_info[0]==3:
		random.seed(seed,version=1)
	else:
		random.seed(seed)
	random.shuffle(pad,random=random.random) # shuffle that gives the same result in py2 and py3
	t = array.array('B',text)
	return [a^b for a,b in zip(t,pad)]

def _init(length=4096):
	"initialize pad with random data"
	p = os.urandom(length)
	f = open(_get_pad_path(),'wb')
	f.write(p)
	# TODO make file private

#########################################################

def encode(s):
	"encode string"
	raw_seed=os.urandom(4)
	seed=struct.unpack('I',raw_seed)
	n=_xor_with_pad(s,seed)
	b = raw_seed+struct.pack(len(n)*'B',*n)
	text = __encode(b)
	text = text.decode() if sys.version_info[0]==3 else text
	return text.replace('=','x')

def decode(s):
	"decode string"
	b = __decode(s.replace('x','=').encode())
	raw_seed,b = b[:4],b[4:]
	seed=struct.unpack('I',raw_seed)
	n = struct.unpack(len(b)*'B',b)
	x = _xor_with_pad(n,seed)
	text = struct.pack(len(x)*'B',*x)
	return text.decode() if sys.version_info[0]==3 else text

#########################################################

if __name__=="__main__":
	if 1:
		if sys.version_info[0]==2:
			print(encode('test'))
		else:
			print(decode('Y6EJGVMBF6YI4xxx'))
	if 0:
		if sys.version_info[0]==3:
			print(encode('test'))
		else:
			print(decode('G4IUAKLCNI6Y2xxx'))
	if 0:
		print(_xor_with_pad('test'))
	if 0:
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
