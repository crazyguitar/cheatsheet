Python asyncio cheatsheet
=========================

What is @asyncio.coroutine?
---------------------------

.. code-block:: python

    import asyncio
    import inspect
    from functools import wraps

    Future = asyncio.futures.Future
    def coroutine(func):
        """Simple prototype of coroutine"""
        @wraps(func)
        def coro(*a, **k):
            res = func(*a, **k)
            if isinstance(res, Future) or inspect.isgenerator(res):
                res = yield from res
            return res
        return coro

    @coroutine
    def foo():
        yield from asyncio.sleep(1)
        print("Hello Foo")

    @asyncio.coroutine
    def bar():
        print("Hello Bar")

    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(foo()),
             loop.create_task(bar())]
    loop.run_until_complete(
         asyncio.wait(tasks))
    loop.close()

output:

.. code-block:: console

    $ python test.py
    Hello Bar
    Hello Foo


What is a Task?
---------------

.. code-block:: python

    # goal: supervise coroutine run state
    # ref: asyncio/tasks.py

    import asyncio
    Future = asyncio.futures.Future

    class Task(Future):
        """Simple prototype of Task"""

        def __init__(self, gen, *,loop):
            super().__init__(loop=loop)
            self._gen = gen
            self._loop.call_soon(self._step)

        def _step(self, val=None, exc=None):
            try:
                if exc:
                    f = self._gen.throw(exc)
                else:
                    f = self._gen.send(val)
            except StopIteration as e:
                self.set_result(e.value)
            except Exception as e:
                self.set_exception(e)
            else:
                f.add_done_callback(
                     self._wakeup)

        def _wakeup(self, fut):
            try:
                res = fut.result()
            except Exception as e:
                self._step(None, e)
            else:
                self._step(res, None)

    @asyncio.coroutine
    def foo():
        yield from asyncio.sleep(3)
        print("Hello Foo")

    @asyncio.coroutine
    def bar():
        yield from asyncio.sleep(1)
        print("Hello Bar")

    loop = asyncio.get_event_loop()
    tasks = [Task(foo(), loop=loop),
             loop.create_task(bar())]
    loop.run_until_complete(
            asyncio.wait(tasks))
    loop.close()

output:

.. code-block:: console

    $ python test.py
    Hello Bar
    hello Foo


What event loop doing? (Without polling)
----------------------------------------

.. code-block:: python

    import asyncio
    from collections import deque

    def done_callback(fut):
        fut._loop.stop()

    class Loop:
        """Simple event loop prototype"""

        def __init__(self):
            self._ready = deque()
            self._stopping = False

        def create_task(self, coro):
            Task = asyncio.tasks.Task
            task = Task(coro, loop=self)
            return task

        def run_until_complete(self, fut):
            tasks = asyncio.tasks
            # get task
            fut = tasks.ensure_future(
                        fut, loop=self)
            # add task to ready queue
            fut.add_done_callback(done_callback)
            # run tasks
            self.run_forever()
            # remove task from ready queue
            fut.remove_done_callback(done_callback)

        def run_forever(self):
            """Run tasks until stop"""
            try:
                while True:
                    self._run_once()
                    if self._stopping:
                        break
            finally:
                self._stopping = False

        def call_soon(self, cb, *args):
            """Append task to ready queue"""
            self._ready.append((cb, args))
        def call_exception_handler(self, c):
            pass

        def _run_once(self):
            """Run task at once"""
            ntodo = len(self._ready)
            for i in range(ntodo):
                t, a = self._ready.popleft() 
                t(*a)

        def stop(self):
            self._stopping = True
            
        def close(self):
            self._ready.clear()

        def get_debug(self):
            return False

    @asyncio.coroutine
    def foo():
        print("Foo")

    @asyncio.coroutine
    def bar():
        print("Bar")

    loop = Loop()
    tasks = [loop.create_task(foo()),
             loop.create_task(bar())]
    loop.run_until_complete(
            asyncio.wait(tasks))
    loop.close()

 output:

.. code-block:: console

    $ python test.py
    Foo 
    Bar

Socket with asyncio
-------------------

.. code-block:: python

    import asyncio
    import socket

    host = 'localhost'
    port = 9527
    loop = asyncio.get_event_loop()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(False)
    s.bind((host, port))
    s.listen(10)

    async def handler(conn):
        while True:
            msg = await loop.sock_recv(conn, 1024)
            if not msg:
                break
            await loop.sock_sendall(conn, msg)
        conn.close()

    async def server():
        while True:
            conn, addr = await loop.sock_accept(s)
            loop.create_task(handler(conn))

    loop.create_task(server())
    loop.run_forever()
    loop.close()

output: (bash 1)

.. code-block:: console

    $ nc localhost 9527
    Hello
    Hello 

output: (bash 2)

.. code-block:: console

    $ nc localhost 9527
    World
    World 


Event Loop with polling
-----------------------

.. code-block:: python

    # using selectors
    # ref: PyCon 2015 - David Beazley

    import asyncio
    import socket
    import selectors
    from collections import deque

    @asyncio.coroutine
    def read_wait(s):
        yield 'read_wait', s

    @asyncio.coroutine
    def write_wait(s):
        yield 'write_wait', s

    class Loop:
        """Simple loop prototype"""

        def __init__(self):
            self.ready = deque() 
            self.selector = selectors.DefaultSelector()

        @asyncio.coroutine
        def sock_accept(self, s):
            yield from read_wait(s)
            return s.accept()

        @asyncio.coroutine
        def sock_recv(self, c, mb):
            yield from read_wait(c)
            return c.recv(mb)

        @asyncio.coroutine
        def sock_sendall(self, c, m):
            while m: 
                yield from write_wait(c)
                nsent = c.send(m)
                m = m[nsent:]

        def create_task(self, coro):
            self.ready.append(coro)

        def run_forever(self):
            while True:
                self._run_once()

        def _run_once(self):
            while not self.ready:
                events = self.selector.select()
                for k, _ in events:
                    self.ready.append(k.data)
                    self.selector.unregister(k.fileobj)

            while self.ready:
                self.cur_t = ready.popleft()
                try:
                    op, *a = self.cur_t.send(None)
                    getattr(self, op)(*a)
                except StopIteration:
                    pass

        def read_wait(self, s):
            self.selector.register(s, selectors.EVENT_READ, self.cur_t)

        def write_wait(self, s):
            self.selector.register(s, selectors.EVENT_WRITE, self.cur_t)

    loop = Loop()
    host = 'localhost'
    port = 9527

    s = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM, 0)
    s.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR, 1)
    s.setblocking(False)
    s.bind((host, port))
    s.listen(10)

    @asyncio.coroutine
    def handler(c):
        while True:
            msg = yield from loop.sock_recv(c, 1024)
            if not msg:
                break
            yield from loop.sock_sendall(c, msg)
        c.close()

    @asyncio.coroutine
    def server():
        while True:
            c, addr = yield from loop.sock_accept(s)
            loop.create_task(handler(c))

    loop.create_task(server())
    loop.run_forever()


Inline callback
---------------

.. code-block:: python

    >>> import asyncio
    >>> async def foo():
    ...     await asyncio.sleep(1)
    ...     return "foo done"
    ... 
    >>> async def bar():
    ...     await asyncio.sleep(.5)
    ...     return "bar done"
    ... 
    >>> async def ker():
    ...     await asyncio.sleep(3)
    ...     return "ker done"
    ... 
    >>> async def task():
    ...     res = await foo()
    ...     print(res)
    ...     res = await bar()
    ...     print(res)
    ...     res = await ker()
    ...     print(res)
    ... 
    >>> loop = asyncio.get_event_loop()
    >>> loop.run_until_complete(task())
    foo done
    bar done
    ker done

Asynchronous Iterator
---------------------

.. code-block:: python

    # ref: PEP-0492
    # need Python >= 3.5

    >>> class AsyncIter:
    ...     def __init__(self, it):
    ...         self._it = iter(it)
    ...     async def __aiter__(self):
    ...         return self
    ...     async def __anext__(self):
    ...         await asyncio.sleep(1)
    ...         try:
    ...             val = next(self._it)
    ...         except StopIteration:
    ...             raise StopAsyncIteration
    ...         return val
    ...
    >>> async def foo():
    ...     it = [1,2,3]
    ...     async for _ in AsyncIter(it):
    ...         print(_)
    ... 
    >>> loop = asyncio.get_event_loop()
    >>> loop.run_until_complete(foo())
    1
    2
    3

Asynchronous context manager
----------------------------

.. code-block:: python

    # ref: PEP-0492
    # need Python >= 3.5

    >>> class AsyncCtxMgr:
    ...     async def __aenter__(self):
    ...         await asyncio.sleep(3)
    ...         print("__anter__")
    ...         return self
    ...     async def __aexit__(self, *exc):
    ...         await asyncio.sleep(1)
    ...         print("__aexit__")
    ...
    >>> async def hello():
    ...     async with AsyncCtxMgr() as m:
    ...         print("hello block")
    ... 
    >>> async def world():
    ...     print("world block")
    ...
    >>> t = loop.create_task(world())
    >>> loop.run_until_complete(hello())
    world block
    __anter__
    hello block
    __aexit__
