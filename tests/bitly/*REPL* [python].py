Python 3.5.0 (default, Sep 14 2015, 02:37:27) 
[GCC 4.2.1 Compatible Apple LLVM 6.1.0 (clang-602.0.53)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> a = [{'a': 1}, {'b': 2}]
>>> sorted(a) 
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unorderable types: dict() < dict()
>>> b = [{'b': 2}, {'a': 1}]