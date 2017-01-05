# What is SMASH?
SMASH is the command language for data analysts and data engineers. It acts as a glue layer for various data processing tools and activities:

* ETL code generation
* remote ETL execution
* local ETL execution (small data volumes)
* reporting automation
* reference data processing
* metadata processing
* data quality checks and measurements
* data profiling
* data cleansing
* data propagation
* notifications

The name is an acronym for 'Simple Modular Automation SHell'.

## syntax

SMASH uses extremely simple grammar:

1. the script is an ordered list of steps (aka sections / procedures)
2. a step consists of:
  * a procedure name (in square brackets)
  * an ordered list of key-value pairs
3. values are assigned to keys using operators:
  * = single-line values
  * <<< multi-line values
  * < values read from files
4. dollar prefixed words are macro-expanded

## examples

```
[let]
name = test

[ssh]
server = devtest
cmd = cd /home/proj/omega && git pull

[email]
to = $name@gmail.com
subject = hello
body <<<
	Hello $name!
	Just wanted to say that the directory of project Omega is up to date.
```

~~~~
[bsv]
tab = stg
names = x y z
data <<<
	1 2 a
	3 4 3

[sql]
code <<<
	drop table if exists stg2;
	create table stg2 as
		select
			x as a,
			y as b,
			z as c
		from stg;
print = select md5(a||b||c),a,b,c from stg2
let cnt = select count(*) from stg2
~~~~

## core built-in procedures

| procedure | reference | short description |
| --- | --- |  --- |
| let | [link](#let) | assign values to macro variables |
| python | [link](#python) | execute python code |
| none | [link](#none) | do nothing - useful for disabling a step |
| use | [link](#use) | use procedures from given directory |
| default | [link](#default) | assign default values to procedure arguments |
| proc | [link](#proc) | create temporary, dynamic procedure |
| loop | [link](#loop) | execute procedure in a loop |

## other built-in procedures

| procedure | reference | short description |
| --- | --- |  --- |
| template | [link](#template) | generate text from a template |
| sql | [link](#sql) | execute sql statements |
| csv | [link](#csv) | coma (or other delimiter) separated values import |
| re | [link](#re) | import regular expression filtered text |
| cmd | [link](#cmd) | execute operating system command |

## why use SMASH?

### code evolution

It's easy to evolve "quick, one-time" scripts into reusable solutions and then into data-driven solutions.

Example

Quick, one-time solution (thanksmsg.smash):
~~~~
[let]
name = Ralph
surname = Kimball
signature = Maciek

[template]
template <<<
	Hello $name $surname!
	I enjoyed your book very much.
	
	regards,
	$signature
~~~~

Reuse of one-time solution (thanks.smash):
~~~~
[thanksmsg]
name = Bill
surname = Inmon
template.outvar = msg

[mail]
to = $mail
subject = Thank You
body = $msg
~~~~

Data-driven solution reusing previous solutions:
~~~~
[sql]
iter ty <<<
	select firstname,surname,email,user
	from thanks
	where sent=0

[loop]
iter = ty
proc = thanks
names = name surname mail signature
~~~~

## SMASH Library Reference



### let

Assign values to macro variables.

Arguments:
> **x** - argument will be stored as macro variable x

Example:
~~~~
[let]
columns = firstname surname title published
authors <<<
	Bill Inmon, Ralph Kimbal, Daniel Linstedt,
	Laurence Corr, Nathan Marz, Lars Ronnback,  Josh Wills
~~~~



### python

Execute python code. SMASH functions: get, get_flag. SMASH objects: args, frame.

Arguments:
> **code** - python code that will be executed

> **let x** - python expression that will be stored as macro variable x

> **print** - python expression that will be printed

> **pprint** - python expression that will be pretty-printed

> **debug** - blank separated list of macro variable names, that will be printed

SMASH functions and objects available in python code:
> **get(name,default='',split=None)** - get argument or variable value

> **get_flag(name,default='')** - get argument or variable boolean value, following values are treated as truth: "yes y true t 1 on" other values are treated as false

> **frame** - current frame object

> **args** - arguments for current section

Example:
~~~~
[python]
code <<<
	print("hello")
	print("world")
~~~~

Example:
~~~~
[let]
radius = 4

[python]
hint = calculate surface area of a circle
code = from math import pi
let areav1 = pi * eval(get('radius'))**2
let areav2 = pi * eval('$radius')**2
debug = radius areav1 areav2
~~~~



### none

Do nothing - useful for disabling a step.

Example:
~~~~
[none]
hint = STEP DISABLED
code = from math import pi
let areav1 = pi * eval(get('radius'))**2
let areav2 = pi * eval('$radius')**2
debug = radius areav1 areav2
~~~~



### use

Use procedures from given directory. The step also checks if the file autoinit.smash is present in given directory and runs it if found. 

Arguments:
> **module** - path to the directory - relative to smash proc directory

> **dir** - path to the directory - absolute or relative to the current directory

Example:
~~~~
[use]
dir = ~/dwh/kimball
~~~~



### default

Assign default values to procedure arguments.

Arguments:
> **proc.arg** - assign this value as a default for argument *arg* of procedure *proc*

Example:
~~~~
[default]
template.clip = 1
sql.db = sqlite('example.db')
~~~~



### proc

Create temporary, dynamic procedure.

Arguments:
> **name** - name for the new dynamic procedure

> **smash** - smash code of the procedure


Example:
~~~~
[proc]
name = hello
smash <<<
	[python]
	code <<<
		print("Hi {0}!".format(get('name')))
		print("See you later.")

[hello]
name = Ralph
~~~~



### loop

Execute procedure in a loop

Arguments:
> **proc** - name of the procedure to call

> **iter** - name of the macro variable with the iterator

> **names** - blank separated names for macro variables from iterator


Example:
~~~~
[sql]
iter authors = select firstname,surname from authors

[loop]
proc = hello
iter = authors
names = name surname
~~~~


### template

Generate text from a template.

Arguments:
> **template** - body of the text template

> **outpath** - path to the output file; if empty standard output will be used

> **outvar** - name of the macro variable that will store the output; if empty it will not be stored as macro variable

> **clip** - if set copies output to the system clipboard (works only on Windows)

Example:
~~~~
[let]
name = Ralph
surname = Kimball
signature <<<
	regards,
	maciek

[template]
template <<<
	Hello $name $surname!
	I enjoyed your book very much.
	$signature
outvar = msg

[python]
debug = msg
~~~~



### sql

Execute sql statements.

Arguments:
> **db** - database connection constructor

> **code** - query code

> **let x** - sql expression that will be stored as macro variable x; only first returned row and column is used

> **iter x** - sql expression that will be stored as iterator x; all returned rows and columns are used

> **print** - sql expression that will be printed

Example:
~~~~
[sql]
code <<<
	create table authors (firstname,surname);
	insert into authors values ('Ralph','Kimball');
	insert into authors values ('Daniel','Linstedt');
	insert into authors values ('Bill','Inmon');
print = select * from authors
iter surnames = select surname from authors
let authors_cnt = select count(*) from authors

[python]
debug = authors_cnt surnames
~~~~



### csv

Coma (or other delimiter) separated values.

Arguments:
> **data** - input data

> **db** - database connection constructor

> **dlm** - delimiter (coma is the default)

> **names** - blank separated list of column names

> **tab** - name of the destination table for storing the data

> **iter** - name of the iterator that will allow access to the data


Example:
~~~~
[csv]
tab = digits
iter = sample
dlm = ;
names = a b c
data <<<
	1;2;3
	4;5;6

[python]
debug = sample

[sql]
print = select a,b,c from digits
~~~~

Example:
~~~~
[csv]
tab = publications
names <<<
	auth_name
	auth_surname
	pub_title
data <<<
	Bill,Inmon,Data Lake Architecture
	Ralph,Kimbal,The Data Warehouse ETL Toolkit
	Daniel,Linstedt,Super Charge Your Data Warehouse
	Laurence,Corr,Agile Data Warehouse Design
	Nathan,Marz,Big Data
	Lars,Ronnback,Anchor Modeling Introduction
	Josh,Wills,What Comes After The Star Schema?

[sql]
print <<<
	select
		substr(auth_name,1,1)||'.'||auth_surname as author,
		pub_title as title
	from publications
~~~~



### re

Import regular expression filtered text.

Arguments:
> **data** - input data

> **find** - regular expression for finding records or columns

> **split** - regular expression for splitting data into records or columns; the result will be stripped

> **exclude** - regular expression for filtering out matching records

> **select** - regular expression for selecting only matching records

> **join** - delimiter for joining columns or records

> **flags** - regular expression flags; defaults to x (VERBOSE) 

> **db** - database connection constructor

> **names** - blank separated list of column names

> **tab** - name of the destination table for storing the data

> **iter** - name of the iterator that will allow access to the data


Example:
~~~~
[re]
data <<<
	Bill Inmon, Ralph Kimbal,,,, Daniel  Linstedt,
	  Laurence Corr,        Nathan    Marz,
	  ,,,,,,,
	Lars Ronnback, 
	Josh  Wills
split = ,
select = .
split = \s+
tab = authors
names = firstname surname

[sql]
print = select * from authors
~~~~

Example:
~~~~
[re]
data <<<
	Bill Inmon, Ralph Kimbal, Daniel  Linstedt,
	  Laurence Corr,        Nathan    Marz,
	  ,,,,,,,
	Lars Ronnback, 
	Josh  Wills
find = (\w+) \s+ (\w+) 
iter = authors

[python]
pprint = get('authors')
~~~~

### cmd

Execute operating system command.

Arguments:
> **cmd** - system command with arguments

> **input** - standard input for the command

Example:
~~~~
[cmd]
cmd = echo CONNECTING TO $host
cmd = $ssh $host $auth $cmd
~~~~

Example:
~~~~
[cmd]
cmd = echo CONNECTING TO $host
input <<<
	cd /proc
	ls
	exit
cmd = $ssh $host $auth
~~~~
