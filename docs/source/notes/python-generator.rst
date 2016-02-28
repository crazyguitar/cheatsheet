===========================
Python generator cheatsheet
===========================

Glossary of Generator
---------------------

.. code-block:: python

    # generator function
    >>> def gen_func():
    ...     yield 5566
    ... 
    >>> gen_func
    <function gen_func at 0x1019273a>

    # generator
    >>> g = gen_func()
    >>> g
    <generator object gen_func at 0x101238fd>
    >>> next(g)
    5566
    >>> next(g)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    StopIteration

    # generator expression
    >>> g = (_ for _ in range(2))
    >>> g
    <generator object <genexpr> at 0x10a9c191>
    >>> next(g)
    0
    >>> next(g)
    1
    >>> next(g)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    StopIteration

Produce value via generator
---------------------------

.. code-block:: python

    >>> def prime(n):
    ...   p = 2
    ...   while n > 0:
    ...     for _ in range(2,p):
    ...       if p % _ == 0:
    ...         break
    ...     else:
    ...       yield p
    ...       n-=1
    ...     p+=1
    ...
    >>> p = prime(3)
    >>> next(p)
    2
    >>> next(p)
    3
    >>> 
    >>> next(p)
    5
    >>> next(p)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    StopIteration
    >>> for _ in prime(5):
    ...   print(_, end=" ")
    ... 
    2 3 5 7 11 >>>

Implement Iterable object via generator
---------------------------------------

.. code-block:: python

    >>> class count(object):
    ...   def __init__(self,n):
    ...     self._n = n
    ...   def __iter__(self):
    ...     n = self._n
    ...     while n>0:
    ...       yield n
    ...       n-=1
    ...   def __reversed__(self):
    ...     n = 0
    ...     while n<self._n:
    ...       yield n
    ...       n+=1
    ... 
    >>> for _ in count(5):
    ...   print(_, end=" ")
    ... 
    5 4 3 2 1 >>> 
    >>> for _ in reversed(count(5)):
    ...   print(_, end=" ")
    ... 
    0 1 2 3 4 >>>

Send message to generator
-------------------------

.. code-block:: python

    >>> def spam():
    ...   msg = yield
    ...   print("Message:",msg)
    ... 
    >>> try:
    ...   g = spam()
    ...   # start generator
    ...   next(g)
    ...   # send message to generator
    ...   g.send("Hello World!")
    ... except StopIteration:
    ...   pass
    ... 
    Message: Hello World!

"yield from" expression
-----------------------

.. code-block:: python

    # delegating gen do nothing(pipe)
    >>> def subgen():
    ...     try:
    ...         yield 9527
    ...     except ValueError:
    ...         print("get value error")
    ... 
    >>> def delegating_gen():
    ...     yield from subgen()
    ...
    >>> g = delegating_gen()
    >>> try: 
    ...     next(g)
    ...     g.throw(ValueError)
    ... except StopIteration:
    ...     print("gen stop")
    ... 
    9527
    get value error
    gen stop

    # yield from + yield from
    >>> import inspect
    >>> def subgen():
    ...     yield from range(5)
    ... 
    >>> def delegating_gen():
    ...     yield from subgen()
    ... 
    >>> g = delegating_gen()
    >>> inspect.getgeneratorstate(g)
    'GEN_CREATED'
    >>> next(g)
    0
    >>> inspect.getgeneratorstate(g)
    'GEN_SUSPENDED'
    >>> g.close()
    >>> inspect.getgeneratorstate(g)
    'GEN_CLOSED'

yield (from) EXPR return RES
----------------------------

.. code-block:: python

    >>> def average():
    ...     total = .0
    ...     count = 0
    ...     avg = None
    ...     while True:
    ...         val = yield 
    ...         if not val:
    ...             break
    ...         total += val
    ...         count += 1
    ...         avg = total / count
    ...     return avg
    ... 
    >>> g = average()
    >>> g = average()
    >>> next(g) # start gen
    >>> g.send(3)
    >>> g.send(5)
    >>> try:
    ...     g.send(None)
    ... except StopIteration as e:
    ...     ret = e.value
    ... 
    >>> ret
    4.0

    # yield from EXP return RES
    >>> def subgen():
    ...     yield 9527
    ... 
    >>> def delegating_gen():
    ...     yield from subgen()
    ...     return 5566
    ...
    >>> try:
    ...     g = delegating_gen()
    ...     next(g)
    ...     next(g)
    ... except StopIteration as _e:
    ...     print(_e.value)
    ... 
    9527
    5566

Generate sequences
------------------

.. code-block:: python

    # get a list via generator
    >>> def chain():
    ...     for _ in 'ab':
    ...         yield _
    ...     for _ in range(3):
    ...         yield _
    ... 
    >>> a = list(chain())
    >>> a
    ['a', 'b', 0, 1, 2]
    # equivalent to 
    >>> def chain():
    ...     yield from 'ab'
    ...     yield range(3)
    ...
    >>> a = list(chain())
    >>> a
    ['a', 'b', range(0, 3)]

What "RES = yield from EXP" actually do?
----------------------------------------

.. code-block:: python

    # ref: pep380
    >>> def subgen():
    ...     for _ in range(3):
    ...         yield _
    ... 
    >>> EXP = subgen()
    >>> def delegating_gen():
    ...   _i = iter(EXP)
    ...   try:
    ...     _y = next(_i)
    ...   except StopIteration as _e:
    ...     RES = _e.value
    ...   else:
    ...     while True:
    ...       _s = yield _y
    ...       try:
    ...         _y = _i.send(_s)
    ...       except StopIteration as _e:
    ...           RES = _e.value
    ...           break
    ... 
    >>> g = delegating_gen()
    >>> next(g)
    0
    >>> next(g)
    1
    >>> next(g)
    2

    # equivalent to
    >>> EXP = subgen()
    >>> def delegating_gen():
    ...     RES = yield from EXP
    ... 
    >>> g = delegating_gen()
    >>> next(g)
    0
    >>> next(g)
    1

Check generator type
--------------------

.. code-block:: python

    >>> from types import GeneratorType
    >>> def gen_func():
    ...     yield 5566
    ... 
    >>> g = gen_func()
    >>> isinstance(g, GeneratorType)
    True
    >>> isinstance(123, GeneratorType)
    False

Check Generator State
---------------------

.. code-block:: python

    >>> import inspect
    >>> def gen_func():
    ...     yield 9527
    ... 
    >>> g = gen_func()
    >>> inspect.getgeneratorstate(g)
    'GEN_CREATED'
    >>> next(g)
    9527
    >>> inspect.getgeneratorstate(g)
    'GEN_SUSPENDED'
    >>> g.close()
    >>> inspect.getgeneratorstate(g)
    'GEN_CLOSED'

Context manager and generator
-----------------------------

.. code-block:: python

    >>> import contextlib
    >>> @contextlib.contextmanager
    ... def mylist():
    ...   try:
    ...     l = [1,2,3,4,5]
    ...     yield l
    ...   finally:
    ...     print("exit scope")
    ... 
    >>> with mylist() as l:
    ...   print(l)
    ... 
    [1, 2, 3, 4, 5]
    exit scope

What @contextmanager actually doing?
------------------------------------

.. code-block:: python

    # ref: PyCon 2014 - David Beazley
    # define a context manager class
    class GeneratorCM(object):
        def __init__(self,gen):
            self._gen = gen
        def __enter__(self):
            return next(self._gen)
        def __exit__(self, *exc_info):
            try:
                if exc_info[0] is None:
                    next(self._gen)
                else:
                    self._gen.throw(*exc_info)
                raise RuntimeError
            except StopIteration:
                return True
            except:
                raise
                
    # define a decorator
    def contextmanager(func):
        def run(*a, **k):
            return GeneratorCM(func(*a, **k))
        return run

    # example of context manager
    @contextmanager
    def mylist():
        try:
            l=[1,2,3,4,5]
            yield l
        finally:
            print "exit scope"

    with mylist() as l:
        print l

output:

.. code-block:: console 

    $ python ctx.py 
    [1, 2, 3, 4, 5]
    exit scope

'yield from' and '__iter__'
---------------------------

.. code-block:: python

    >>> class FakeGen:
    ...     def __iter__(self):
    ...         n = 0
    ...         while True:
    ...             yield n
    ...             n += 1
    ...     def __reversed(self):
    ...         n = 9527
    ...         while True:
    ...            yield n 
    ...            n -= 1
    ... 
    >>> def spam():
    ...     yield from FakeGen()
    ... 
    >>> s = spam()
    >>> next(s)
    0
    >>> next(s)
    1
    >>> next(s)
    2
    >>> next(s)
    3
    >>> def reversed_spam():
    ...     yield from reversed(FakeGen())
    ... 
    >>> g = reversed_spam()
    >>> next(g)
    9527
    >>> next(g)
    9526
    >>> next(g)
    9525

"yield from == await" expression
--------------------------------

.. code-block:: python

    # "await" include in pyhton3.5
    import asyncio
    import socket

    # set socket and event loop
    loop = asyncio.get_event_loop()
    host = 'localhost'
    port = 5566
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM,0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    sock.setblocking(False)
    sock.bind((host, port))
    sock.listen(10)

    @asyncio.coroutine
    def echo_server():
        while True:
            conn, addr = yield from loop.sock_accept(sock)
            loop.create_task(handler(conn))

    @asyncio.coroutine
    def handler(conn):
        while True:
            msg = yield from loop.sock_recv(conn, 1024)
            if not msg:
                break
            yield from loop.sock_sendall(conn, msg)
        conn.close()

    # equal to
    async def echo_server():
        while True:
            conn, addr = await loop.sock_accept(sock)
            loop.create_task(handler(conn))

    async def handler(conn):
        while True:
            msg = await loop.sock_recv(conn, 1024)
            if not msg:
                break
            await loop.sock_sendall(conn, msg)
        conn.close()

    loop.create_task(echo_server())
    loop.run_forever()

output: (bash 1)

.. code-block:: console

    $ nc localhost 5566
    Hello
    Hello


output: (bash 2)

.. code-block:: console

    $ nc localhost 5566
    World
    World


Closure in Python - using generator
-----------------------------------

.. code-block:: python

    # nonlocal version
    >>> def closure():
    ...     x = 5566
    ...     def inner_func():
    ...         nonlocal x
    ...         x += 1
    ...         return x
    ...     return inner_func
    ... 
    >>> c = closure()
    >>> c()
    5567
    >>> c()
    5568
    >>> c()
    5569

    # class version
    >>> class Closure:
    ...     def __init__(self):
    ...         self._x = 5566
    ...     def __call__(self):
    ...         self._x += 1
    ...         return self._x
    ... 
    >>> c = Closure()
    >>> c()
    5567
    >>> c()
    5568
    >>> c()
    5569

    # generator version (best)
    >>> def closure_gen():
    ...     x = 5566
    ...     while True:
    ...         x += 1
    ...         yield x
    ... 
    >>> g = closure_gen()
    >>> next(g)
    5567
    >>> next(g)
    5568
    >>> next(g)
    5569


Implement a simple scheduler
----------------------------

.. code-block:: python

    # idea: write an event loop(scheduler)
    >>> def fib(n):
    ...   if n<=2:
    ...     return 1
    ...   return fib(n-1)+fib(n-2)
    ... 
    >>> def g_fib(n):
    ...   for _ in range(1,n+1):
    ...     yield fib(_)
    ... 
    >>> from collections import deque
    >>> t = [g_fib(3),g_fib(5)]
    >>> q = deque()
    >>> q.extend(t)
    >>> def run():
    ...   while q:
    ...     try:
    ...       t = q.popleft()
    ...       print(next(t))
    ...       q.append(t)
    ...     except StopIteration:
    ...       print("Task done")
    ... 
    >>> run()
    1
    1
    1
    1
    2
    2
    Task done
    3
    5
    Task done

Simple round-robin with blocking
--------------------------------

.. code-block:: python

    # ref: PyCon 2015 - David Beazley
    # skill: using task and wait queue
    from collections import deque
    from select import select
    import socket

    tasks = deque()
    w_read = {}
    w_send = {}

    def run():
       while any([tasks,w_read,w_send]):
          while not tasks:
             # polling tasks
             can_r,can_s,_ = select(
                   w_read,w_send,[])
             for _r in can_r:
                tasks.append(w_read.pop(_r))
             for _w in can_s:
                tasks.append(w_send.pop(_w))
          try:
             task = tasks.popleft()
             why,what = next(task)
             if why == 'recv':
                w_read[what] = task 
             elif why == 'send':
                w_send[what] = task 
             else:
                raise RuntimeError
          except StopIteration:
             pass

    def server():
       host = ('localhost',5566)
       sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       sock.bind(host)
       sock.listen(5)
       while True:
          # tell scheduler want block
          yield 'recv', sock 
          conn,addr = sock.accept()
          tasks.append(client_handler(conn))

    def client_handler(conn):
       while True:
          # tell scheduler want block
          yield 'recv', conn
          msg = conn.recv(1024)
          if not msg:
             break
          # tell scheduler want block
          yield 'send', conn
          conn.send(msg)
       conn.close()

    tasks.append(server())
    run()

simple round-robin with blocking and non-blocking
-------------------------------------------------

.. code-block:: python

    # this method will cause blocking hunger
    from collections import deque
    from select import select
    import socket

    tasks = deque()
    w_read = {}
    w_send = {}

    def run():
       while any([tasks,w_read,w_send]):
          while not tasks:
             # polling tasks
             can_r,can_s,_ = select(
                   w_read,w_send,[])
             for _r in can_r:
                tasks.append(w_read.pop(_r))
             for _w in can_s:
                tasks.append(w_send.pop(_w))
          try:
             task = tasks.popleft()
             why,what = next(task)
             if why == 'recv':
                w_read[what] = task 
             elif why == 'send':
                w_send[what] = task 
             elif why == 'continue':
                print what
                tasks.append(task)
             else:
                raise RuntimeError
          except StopIteration:
             pass

    def fib(n):
       if n<=2:
          return 1
       return fib(n-1)+fib(n-2)

    def g_fib(n):
       for _ in range(1,n+1):
          yield 'continue', fib(_)
    tasks.append(g_fib(15))

    def server():
       host = ('localhost',5566)
       sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       sock.bind(host)
       sock.listen(5)
       while True:
          yield 'recv', sock 
          conn,addr = sock.accept()
          tasks.append(client_handler(conn))

    def client_handler(conn):
       while True:
          yield 'recv', conn
          msg = conn.recv(1024)
          if not msg:
             break
          yield 'send', conn
          conn.send(msg)
       conn.close()

    tasks.append(server())
    run()
