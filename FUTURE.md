# Future changes in SMASH

## changes overview

* unified input and output (input / ?output? operators)
* step pipelining (string / iterator)
* better step decomposition
* default argument (empty arg name)
* substitution only templates (use input from code block for logic)
* sqlite as the only internal db
* better variable scoping
* no duplicates of arg names (?except for input and output?)
* input / output caching
* optional step labels or tags

## input operators

| operator | name              | description | multi-line |
| --- | ---------------------- | ----------- | --- |
| <<< | from python output     |  | yes, ignore text between operator and newline, dedent the rest of lines |
|  << | from python expression |  | no |
|   < | from file              |  | no |
|   = | from text              |  | yes, dedent all lines and left-strip the first one |

## output operators

| operator | name            | description |
| --- | -------------------- | ----------- |
| >>> | to python code block |  |
|  >> | to smash variable    |  |
|   > | to file              |  |


## notes

~~~~

[write] <<
	1  2  3
	4  5  6
	7  8  9

[tsv]
head = no
cols = a b c

[insert]
tab = my_numbers

[sql]
=	select b*c
	from my_numbers
	where a > 1
	;

[echo]

[python] 
=	def row(r): return "(${0})".format(r)
	print(','.join(map(row,prev.out)))
out >> test
append test << this.out

~~~~
