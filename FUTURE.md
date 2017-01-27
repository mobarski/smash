# Future changes in SMASH

## changes overview

* unified input and output (input/output operators)
* step pipelining (string / iterator)
* better step decomposition
* aux operators
* default argument (empty arg name)
* substitution only templates (use input from code block for logic)
* sqlite as the only internal db
* better variable scoping
* no duplicates of arg names

## input operators

| operator | name              | description | multi-line |
| --- | ---------------------- | ----------- | --- |
| <<< | from python output     |  | yes |
|  << | from python expression |  | no  |
|   < | from file              |  | no  |
|   = | from text              |  | yes |

## output operators

| operator | name            | description |
| --- | -------------------- | ----------- |
| >>> | to python code block |  |
|  >> | to smash variable    |  |
|   > | to file              |  |

## aux operators

| operator | name           | description |
| --- | ------------------- | ----------- |
| ... | execute python code |  |

