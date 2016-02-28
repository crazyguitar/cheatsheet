Python Design Pattern in C
==========================

Decorator in C
--------------

Python

.. code-block:: python

    >>> def decorator(func):
    ...     def wrapper(*args, **kwargs):
    ...         print("I am decorator")
    ...         ret = func(*args, **kwargs)
    ...         return ret
    ...     return wrapper
    ...
    >>> @decorator
    ... def hello(str):
    ...     print("Hello {0}".format(str))
    ... 
    >>> @decorator
    ... def add(a,b):
    ...     print("add %d+%d=%d" % (a,b,a+b))
    ...     return a+b
    ... 
    >>> hello("KerKer")
    I am decorator
    Hello KerKer
    >>> add(1,2)
    I am decorator
    add 1+2=3
    3

C

.. code-block:: c

    #include <stdio.h>

    #define DECORATOR(t, f, declar, input) \
       t decor_##f(declar) { \
          printf("I am decorator\n"); \
          return f(input);\
       }
    #define FUNC_DEC(func, ...) \
       decor_##func(__VA_ARGS__)

    // Original function
    void hello(char *str) {
       printf("Hello %s\n", str);
    }

    int add(int a, int b) {
       printf("add %d + %d = %d\n",a,b,a+b);
       return a+b;
    }
    // Patch function
    #define DECLAR    char *str
    #define INPUT     str
    DECORATOR(void, hello, DECLAR, INPUT)
    #undef DECLAR
    #undef INPUT

    #define DECLAR    int a, int b
    #define INPUT     a,b 
    DECORATOR(int, add, DECLAR, INPUT)
    #undef DECLAR
    #undef INPUT

    int main(int argc, char *argv[]) {
       FUNC_DEC(hello, "KerKer");
       FUNC_DEC(add,1,2);

       return 0;
    }

output:

.. code-block:: console

    $ gcc example.c
    $ ./a.out
    I am decorator
    Hello KerKer
    I am decorator
    add 1 + 2 = 3

A Set of Functions
------------------

Python

.. code-block:: python

    >>> def func_1():
    ...     print "Hello"
    ... 
    >>> def func_2():
    ...     print "World"
    ... 
    >>> def func_3():
    ...     print "!!!"
    ... 
    >>> s = [func_1,func_2,func_3]
    >>> for _ in s: _()
    ... 
    Hello
    World
    !!!

C

.. code-block:: c

    #include <stdio.h>

    typedef void (*func)(void);

    enum func_id{
       FUNC_1,FUNC_2,FUNC_3
    };

    void func_1() {
       printf("Hello ");
    }
    void func_2() {
       printf("World ");
    }
    void func_3() {
       printf("!!!\n");
    }

    func gFuncTable[] = {
       func_1,func_2,func_3
    };

    int main(int argc, char *argv[]) {
       gFuncTable[FUNC_1]();
       gFuncTable[FUNC_2]();
       gFuncTable[FUNC_3]();

       return 0;
    }

Closure in C
------------

Python

.. code-block:: python

    # implement via __call__
    >>> class closure(object):
    ...     def __init__(self):
    ...         self.val = 5566
    ...     def __call__(self,var):
    ...         self.val += var
    ... 
    >>> c = closure()
    >>> c(9527)
    >>> print c.val
    15093
    # using "global" keyword 
    >>> x = 0
    >>> def closure(val):
    ...     def wrapper():
    ...         global x 
    ...         x += val
    ...         print x
    ...     wrapper()
    ... 
    >>> closure(5566)
    5566
    >>> closure(9527)
    15093
    # using "nonlocal" (only in python3)
    >>> def closure(val):
    ...     x = 0
    ...     def wrapper():
    ...         nonlocal x
    ...         x += val
    ...         print(x)
    ...     wrapper()
    ... 
    >>> closure(5566)
    5566
    >>> closure(9527)
    9527

C

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>

    typedef struct Closure {
       int val;
       void (*add) (struct Closure **, int);
    }closure;

    void add_func(closure **c, int var) {
       (*c)->val += var;
    }

    int main(int argc, char *argv[]) {
       closure *c = NULL;
       c = malloc(sizeof(closure));
       c->val = 5566;
       c->add = add_func;
       c->add(&c,9527);
       printf("result: %d\n",c->val);

       return 0;
    }


Generator
---------

Python

.. code-block:: python

    >>> def gen():
    ...     var = 0
    ...     while True:
    ...         var += 1
    ...         yield var
    ...
    >>> g = gen()
    >>> for _ in range(3):
    ...     print next(g),
    ... 
    1 2 3

C

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>

    struct gen {
       int (*next) (struct gen *);
       int var;
    };

    int next_func(struct gen *g) {
       printf("var = %d\n",g->var);
       g->var +=1;
       return g->var;
    }

    struct gen * new_gen() {
       struct gen *g = NULL;
       g = (struct gen*) 
             malloc(sizeof(struct gen));
       g->var = 0;
       g->next = next_func;
       return g;
    }

    int main(int argc, char *argv[]) {
       struct gen *g = new_gen();
       int i = 0;
       for (i=0;i<3;i++) {
          printf("gen var = %d\n",g->next(g));
       }
       return 0;
    }

Context Manager in C
--------------------

Python

.. code-block:: python

    >>> class CtxManager(object):
    ...     def __enter__(self):
    ...         self._attr = "KerKer"
    ...         return self._attr
    ...     def __exit__(self,*e_info):
    ...         del self._attr
    ... 
    >>> with CtxManager() as c:
    ...     print c
    ... 
    KerKer

C

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>

    #define ENTER(type,ptr,len) \
       printf("enter context manager\n");\
       ptr = malloc(sizeof(type)*len);\
       if (NULL == ptr) { \
          printf("malloc get error\n");\
          goto exit;\
       }\

    #define EXIT(ptr) \
    exit:\
       printf("exit context manager\n");\
       if (NULL != ptr) {\
          free(ptr);\
          ptr = NULL;  \
       }\

    #define CONTEXT_MANAGER(t, p, l,...){\
       ENTER(t,p,l)\
       __VA_ARGS__ \
       EXIT(p)\
    }

    int main(int argc, char *argv[]) {
       char *ptr;
       CONTEXT_MANAGER(char, ptr, 128,
          sprintf(ptr, "Hello World");  
          printf("%s\n",ptr);
       );
       printf("ptr = %s\n",ptr);
       return 0;
    }

Tuple in C
----------

Python

.. code-block:: python

    >>> a = ("Hello","World",123)
    >>> for _ in a: print _,
    ... 
    Hello World 123

C

.. code-block:: c

    #include <stdio.h>

    int main(int argc, char *argv[]) {
       int a = 123;
       void * const x[4] = {"Hello",
                            "World",&a};
       printf("%s %s, %d\n",x[0],x[1],*(int *)x[2]);
       return 0;
    }

Error Handling
--------------

Python

.. code-block:: python

    >>> import os
    >>> def spam(a,b):
    ...     try:
    ...         os.listdir('.')
    ...     except OSError:
    ...         print "listdir get error"
    ...         return
    ...     try:
    ...         a/b
    ...     except ZeroDivisionError:
    ...         print "zero division"
    ...         return
    ... 
    >>> spam(1,0)
    zero division
    # single exit -> using decorator
    >>> import time
    >>> def profile(func):
    ...     def wrapper(*args, **kwargs):
    ...         s = time.time()
    ...         ret = func(*args, **kwargs)
    ...         e = time.time()
    ...         print e - s
    ...         return ret
    ...     return wrapper
    ...
    >>> @profile
    ... def spam(a,b):
    ...     try:
    ...         os.listdir('.')
    ...     except OSError:
    ...         return
    ...     try:
    ...         a/b
    ...     except ZeroDivisionError:
    ...         return
    ... 
    >>> spam(1,0)
    0.000284910202026

C

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>

    int main(int argc, char *argv[]) {
       int ret = -1;
       char *ptr;
       ptr = malloc(sizeof(char)*128);
       if (NULL == ptr) {
          perror("malloc get error");
          goto exit;
       }
       strcpy(ptr,"KerKer");
       printf("%s\n", ptr);
       ret = 0;
    exit:
       if (ptr) {
          free(ptr);
          ptr = NULL;
       } 
       return ret;
    }

Keyword Arguments in C
----------------------

Python

.. code-block:: python

    >>> def f(str_, float_,int_=0):
    ...     print(str_, float_, int_)
    ... 
    >>> f("KerKer",2.0,2)
    KerKer 2.0 2
    >>> f("HaHa",3.)
    HaHa 3.0 0

C

.. code-block:: c

    #include <stdio.h>

    #define FUNC(...) \
       base_func((struct input ){.var=0, ##__VA_ARGS__});

    struct input {
       char *str;
       int var;
       double dvar;
    };

    void base_func(struct input in){
       printf("str = %s, var = %d" 
          ", dvar = %lf\n",
          in.str, in.var,in.dvar);
    }

    int main(int argc, char *argv[]) {
       FUNC(.str="KerKer", 2.0);
       FUNC(2, .str="KerKer");
       FUNC(.var=10, .dvar=2.0, .str="HAHA");
       return 0;
    }

Function "MAP"
--------------

Python

.. code-block:: python

    >>> x = [1,2,3,4,5]
    >>> y = map(lambda x:2*x, x)
    >>> print y
    [2, 4, 6, 8, 10]
    #or
    >>> x = [1,2,3,4,5]
    >>> y = [2*_ for _ in x]
    >>> print y
    [2, 4, 6, 8, 10]

C

.. code-block:: c

    #include <stdio.h>

    #define MAP(func, src, dst, len) \
       do {\
          unsigned i=0;\
          for(i=0; i<len; i++) {\
             dst[i] = func(src[i]);\
          }\
       }while(0);

    int multi2(int a) {
       return 2*a;
    }

    int main(int argc, char *argv[]) {
       int x[] = {1,2,3,4,5};
       int y[5] = {0};
       int i = 0;

       MAP(multi2, x, y, 5);
       for(i=0;i<5;i++) {
          printf("%d ",y[i]);
       }
       printf("\n");
    }

foreach in C
------------

Python

.. code-block:: python

    >>> x = ["Hello","World","!!!"]
    >>> for _ in x:print _,
    ... 
    Hello World !!!

C

.. code-block:: c

    #include <stdio.h>

    #define foreach(it, x,...) \
       for(char **it=x;*it;it++) {__VA_ARGS__}

    int main(int argc, char *argv[]) {
       char *x[] = {"Hello","World",
                    "!!!",NULL};
       foreach(it,x,
          printf("%s ",*it);  
       )
       printf("\n");
       return 0;
    }

Simple OOP in C
---------------

Python

.. code-block:: python

    # common declaration
    >>> class obj(object):
    ...     def __init__(self):
    ...         self.a = 0
    ...         self.b = 0
    ...     def add(self):
    ...         return self.a + self.b
    ...     def sub(self):
    ...         return self.a - self.b
    ...     
    >>> o = obj()
    >>> o.a = 9527
    >>> o.b = 5566
    >>> o.add()
    15093
    >>> o.sub()
    3961
    # patch class (more like ooc)
    >>> class obj(object):
    ...     def __init__(self):
    ...         self.a = 0
    ...         self.b = 0
    ... 
    >>> def add(self):
    ...     return self.a+self.b
    ... 
    >>> def sub(self):
    ...     return self.a - self.b
    ... 
    >>> obj.add = add
    >>> obj.sub = sub
    >>> o = obj()
    >>> o.a = 9527
    >>> o.b = 5566
    >>> o.add()
    15093
    >>> o.sub()
    3961

C

.. code-block:: c

    #include <stdio.h>
    #include <stdlib.h>

    typedef struct object Obj;
    typedef int (*func)(Obj *);

    struct object {
       int a;
       int b;
       // virtual
       func add; 
       func sub;
    };
    int add_func(Obj *self) {
       return self-&t;a + self->b;
    }
    int sub_func(Obj *self) {
       return self->a - self->b;
    }
    int init_obj(Obj **self) {
       *self = malloc(sizeof(Obj));
       if (NULL == *self) {
          return -1;
       }
       (*self)->a = 0;
       (*self)->b = 0;
       (*self)->add = add_func;
       (*self)->sub = sub_func;
       return 0;
    }

    int main(int argc, char *argv[]) {
       Obj *o = NULL;
       init_obj(&o);
       o->a = 9527;
       o->b = 5566;
       printf("add = %d\n",o->add(o));
       printf("sub = %d\n",o->sub(o));
       return 0;
    }
