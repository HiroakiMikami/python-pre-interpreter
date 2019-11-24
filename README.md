python-pre-interpreter
===

Generous Python Interpreter inspired by [HMMMML2](https://miyashita.com/projects/hmmmml2-超好意的に解釈するコンパイラ/).


Examples
---

### Case 1 (valid program)

```bash
$ cat examples/sample0.py
print(10)
$ ppi examples/sample0.py
```

### Case 2 (Equal)

```bash
$ cat examples/sample1.py
a = 10
if a = 1:
    print("1")
else:
    print("not 1")
$ ppi examples/sample1.py
all = 10
if all == 1:
    print("1")
else:
    print("not 1")

Patches:
  Patch(range=Range(start=0, end=1), text='all')
  Patch(range=Range(start=3, end=4), text='all')
  Patch(range=Range(start=5, end=6), text='==')
Accept this patch? [Y/n]y
not 1
```

### Case 3 (Spell miss)

```bash
$ cat examples/sample2.py
ptint(10)
$ ppi examples/sample2.py
print(10)

Patches:
  Patch(range=Range(start=0, end=5), text='print')
Accept this pa
```

### Case 4 (forget :)

```bash
$ cat examples/sample3.py
if True
    print(True)
$ ppi examples/sample3.py
if True:
    print(True)

Patches:
  Patch(range=Range(start=-1, end=-1), text=':')
Accept this patch? [Y/n]y
True
```

### Case 5 (indent)

```bash
$ cat examples/sample4.py
if True:
print(True)
$ ppi examples/sample4.py
if True:
    print(True)

Patches:
  Patch(range=Range(start=0, end=0), text='    ')
Accept this patch? [Y/n]y
True
```

### Case 6 (complex case)

```bash
$ cat example/sample5.py
dfe add(xs)
return sum(xs)

print(add([1, 2, 3]))
$ ppi example/sample5.py
def add(xs):
    return sum(xs)

print(add([1, 2, 3]))

Patches:
  Patch(range=Range(start=0, end=3), text='def')
  Patch(range=Range(start=-1, end=-1), text=':')
  Patch(range=Range(start=0, end=0), text='    ')
Accept this patch? [Y/n]y
6
```