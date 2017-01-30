# Future changes in SMASH

## changes overview

* simplicity over performance
* unified input and output (input / ?output? operators)
* step pipelining (string / iterator)
* better step decomposition
* default argument (empty arg name)
* substitution only templates (use input from code block for logic)
* sqlite as the only internal db
* better variable scoping
* no duplicates of arg names (?except for input and output?)
* input / output / error capture and caching
* optional step labels or tags
* switch documentation to .rst format?

## strong points

* no external dependencies
* runs on python2 and python3

## input operators

| operator | name              | description | multi-line | variables |
| --- | ---------------------- | ----------- | --- | --- |
| <<< | from python output     |  | yes, ignore text between operator and newline, dedent the rest of lines | no |
|  << | from python expression |  | no | no |
|   < | from file              |  | no | yes - in both file name and file content |
|   = | from text              |  | yes, dedent all lines and left-strip the first one | yes |

## output operators

| operator | name            | description |
| --- | -------------------- | ----------- |
| >>> | to python function / code block |  |
|  >> | to smash variable    |  |
|   > | to file              |  |


## notes

~~~~

[write]
	1  2  3
	4  5  6
	7  8  9

[tsv]
head = no
cols = a b c

[insert]
tab = my_numbers

[sql]
	select b*c
	from my_numbers
	where a > 1
	;

[echo]

[python] 
	def row(r): return "(${0})".format(r)
	print(','.join(map(row,prev.out)))
out >> test
append test << this.out

out >>> var('test')

[cmd] ssh $host $auth -m commit.sh 

~~~~
