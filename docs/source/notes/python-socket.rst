========================
Python socket cheatsheet
========================

Get Hostname
------------

.. code-block:: python

    >>> import socket
    >>> socket.gethostname()
    'MacBookPro-4380.local'
    >>> hostname = socket.gethostname()
    >>> socket.gethostbyname(hostname)
    '172.20.10.4'
    >>> socket.gethostbyname('localhost')
    '127.0.0.1'

Simple TCP Echo Server
----------------------

.. code-block:: python

    import socket

    class Server(object):
        def __init__(self,host,port):
            self._host = host
            self._port = port
        def __enter__(self):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            sock.bind((self._host,self._port))
            sock.listen(10)
            self._sock = sock
            return self._sock 
        def __exit__(self,*exc_info):
            if exc_info[0]:
                import traceback
                traceback.print_exception(*exc_info)
            self._sock.close()
          
    if __name__ == '__main__':
        host = 'localhost'
        port = 5566
        with Server(host,5566) as s:
            while True:
                conn, addr = s.accept()
                msg = conn.recv(1024)
                conn.send(msg)
                conn.close()

output:

.. code-block:: console

    $ nc localhost 5566
    Hello World 
    Hello World

Simple TCP Echo Server Via SocketServer
---------------------------------------

.. code-block:: python

    >>> import SocketServer
    >>> bh = SocketServer.BaseRequestHandler
    >>> class handler(bh):
    ...   def handle(self):
    ...     data = self.request.recv(1024)
    ...     print self.client_address
    ...     self.request.sendall(data)
    ... 
    >>> host = ('localhost',5566)
    >>> s = SocketServer.TCPServer(
    ...   host, handler)
    >>> s.serve_forever()

 output:

.. code-block:: console

    $ nc -u localhost 5566
    Hello World
    Hello World

Simple UDP Echo Server
----------------------

.. code-block:: python

    import socket

    class UDPServer(object):
        def __init__(self,host,port):
            self._host = host
            self._port = port

        def __enter__(self):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((self._host,self._port))
            self._sock = sock
            return sock
       def __exit__(self,*exc_info):
            if exc_info[0]:
                import traceback
                traceback.print_exception(*exc_info)
            self._sock.close()

    if __name__ == '__main__':
        host = 'localhost'
        port = 5566
        with UDPServer(host,port) as s:
            while True:
                msg, addr = s.recvfrom(1024)
                s.sendto(msg, addr)

output:

.. code-block:: console 

    $ nc -u localhost 5566
    Hello World
    Hello World


Simple UDP Echo Server Via SocketServer
---------------------------------------

.. code-block:: python

    >>> import SocketServer
    >>> bh = SocketServer.BaseRequestHandler
    >>> class handler(bh):
    ...   def handle(self):
    ...     m,s = self.request
    ...     s.sendto(m,self.client_address)
    ...     print self.client_address
    ... 
    >>> host = ('localhost',5566)
    >>> s = SocketServer.UDPServer(
    ...   host, handler)
    >>> s.serve_forever()

output:

.. code-block:: console

    $ nc -u localhost 5566
    Hello World
    Hello World


Simple UDP client - Sender
--------------------------

.. code-block:: python

    >>> import socket
    >>> import time
    >>> sock = socket.socket(
    ...   socket.AF_INET,
    ...   socket.SOCK_DGRAM)
    >>> host = ('localhost',5566)
    >>> while True:
    ...   sock.sendto("Hello\n",host)
    ...   time.sleep(5)
    ...

output:

.. code-block:: console

    $ nc -lu localhost 5566
    Hello
    Hello

Broadcast UDP Packets
---------------------

.. code-block:: python

    >>> import socket
    >>> import time
    >>> sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    >>> sock.bind(('',0))
    >>> sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
    >>> while True:
    ...   m = '{0}\n'.format(time.time())
    ...   sock.sendto(m,('<broadcast>',5566))
    ...   time.sleep(5)
    ...

output:

.. code-block:: console

    $ nc -k -w 1 -ul 5566
    1431473025.72

Simple UNIX Domain Socket
-------------------------

.. code-block:: python

    import socket
    import contextlib
    import os

    @contextlib.contextmanager
    def DomainServer(addr):
        try:
            if os.path.exists(addr):
                os.unlink(addr)
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.bind(addr)
            sock.listen(10)
            yield sock
        finally:
            sock.close()
            if os.path.exists(addr):
                os.unlink(addr)

    addr = "./domain.sock"
    with DomainServer(addr) as sock:
        while True:
            conn, _ = sock.accept()
            msg = conn.recv(1024)
            conn.send(msg)
            conn.close()

output:

.. code-block:: console

    $ nc -U ./domain.sock
    Hello
    Hello

Simple Asynchronous TCP Server - Thread
---------------------------------------

.. code-block:: python

    >>> from threading import Thread
    >>> import socket
    >>> def work(conn):
    ...   while True:
    ...     msg = conn.recv(1024)
    ...     conn.send(msg)
    ...
    >>> sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    >>> sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    >>> sock.bind(('localhost',5566))
    >>> sock.listen(5)
    >>> while True:
    ...   conn,addr = sock.accept()
    ...   t=Thread(target=work,args=(conn,))
    ...   t.daemon=True
    ...   t.start()
    ...

output: (bash 1)

.. code-block:: console

    $ nc localhost 5566
    Hello
    Hello

output: (bash 2)

.. code-block:: console

    $ nc localhost 5566
    Ker Ker
    Ker Ker

Simple Asynchronous TCP Server - select
---------------------------------------

.. code-block:: python

    from select import select
    import socket

    host = ('localhost',5566)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    sock.bind(host)
    sock.listen(5)
    rl = [sock]
    wl = []
    ml = {}
    try:
        while True:
            r, w, _ = select(rl,wl,[])
            # process ready to ready
            for _ in r:
                if _ == sock:
                    conn, addr = sock.accept()
                    rl.append(conn)
                else:
                    msg = _.recv(1024)
                    ml[_.fileno()] = msg
                    wl.append(_) 
            # process ready to write
            for _ in w:
                msg = ml[_.fileno()] 
                _.send(msg)
                wl.remove(_)
                del ml[_.fileno()]
    except:
        sock.close()

output: (bash 1)

.. code-block:: console

    $ nc localhost 5566
    Hello
    Hello

output: (bash 2)

.. code-block:: console

    $ nc localhost 5566
    Ker Ker
    Ker Ker

High-Level API - selectors
--------------------------

.. code-block:: python

    # Pyton3.4+ only
    # Reference: selectors 
    import selectors
    import socket
    import contextlib

    @contextlib.contextmanager
    def Server(host,port):
       try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host,port))
            s.listen(10)
            sel = selectors.DefaultSelector()
            yield s, sel
        except socket.error:
            print("Get socket error")
            raise
        finally:
            if s:
                s.close()

    def read_handler(conn, sel):
        msg = conn.recv(1024) 
        if msg:
            conn.send(msg)
        else:
            sel.unregister(conn)
            conn.close()

    def accept_handler(s, sel):
        conn, _ = s.accept()
        sel.register(conn, selectors.EVENT_READ, read_handler)

    host = 'localhost'
    port = 5566
    with Server(host, port) as (s,sel):
        sel.register(s, selectors.EVENT_READ, accept_handler)
        while True:
            events = sel.select()
            for sel_key, m in events:
                handler = sel_key.data
                handler(sel_key.fileobj, sel)

output: (bash 1)

.. code-block:: console

    $ nc localhost 5566
    Hello 
    Hello

output: (bash 1)

.. code-block:: console

    $ nc localhost 5566
    Hi
    Hi

"socketpair" - Similar to PIPE
------------------------------

.. code-block:: python

    import socket
    import os
    import time

    c_s, p_s = socket.socketpair()
    try:
        pid = os.fork()
    except OSError:
        print "Fork Error"
        raise

    if pid:
        # parent process
        c_s.close()
        while True:
            p_s.sendall("Hi! Child!")
            msg = p_s.recv(1024)
            print msg
            time.sleep(3)
        os.wait()
    else:
        # child process
        p_s.close()
        while True:
            msg = c_s.recv(1024)
            print msg
            c_s.sendall("Hi! Parent!")

.. code-block:: console

    $ python ex.py
    Hi! Child!
    Hi! Parent!
    Hi! Child!
    Hi! Parent!
    ...
