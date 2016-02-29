=======================
Python C API cheatsheet
=======================

PyObject header
---------------

.. code-block:: c

    // ref: python source code
    // Python/Include/object.c
    #define _PyObject_HEAD_EXTRA \
        struct _object *_ob_next;\
        struct _object *_ob_prev;

    #define PyObject_HEAD    \
        _PyObject_HEAD_EXTRA \
        Py_ssize_t ob_refcnt;\
        struct _typeobject *ob_type;

Python C API Template
---------------------

C API source
~~~~~~~~~~~~

.. code-block:: c

    #include <Python.h>

    typedef struct {
        PyObject_HEAD
    } spamObj;

    static PyTypeObject spamType = {
        PyObject_HEAD_INIT(&PyType_Type)
        0,                  //ob_size
        "spam.Spam",        //tp_name
        sizeof(spamObj),    //tp_basicsize
        0,                  //tp_itemsize
        0,                  //tp_dealloc
        0,                  //tp_print
        0,                  //tp_getattr
        0,                  //tp_setattr
        0,                  //tp_compare
        0,                  //tp_repr
        0,                  //tp_as_number
        0,                  //tp_as_sequence
        0,                  //tp_as_mapping
        0,                  //tp_hash
        0,                  //tp_call
        0,                  //tp_str
        0,                  //tp_getattro
        0,                  //tp_setattro
        0,                  //tp_as_buffer
        Py_TPFLAGS_DEFAULT, //tp_flags
        "spam objects",     //tp_doc
    };

    static PyMethodDef spam_methods[] = {
        {NULL}  /* Sentinel */
    };

    /* declarations for DLL import */
    #ifndef PyMODINIT_FUNC
    #define PyMODINIT_FUNC void
    #endif

    PyMODINIT_FUNC 
    initspam(void)
    {
        PyObject *m;
        spamType.tp_new = PyType_GenericNew;
        if (PyType_Ready(&spamType) < 0) {
            goto END;
        }
        m = Py_InitModule3("spam", spam_methods, "Example of Module");
        Py_INCREF(&spamType);
        PyModule_AddObject(m, "spam", (PyObject *)&spamType);
    END:
        return;
    }

Prepare setup.py
~~~~~~~~~~~~~~~~

.. code-block:: python

    from distutils.core import setup
    from distutils.core import Extension

    setup(name="spam",
          version="1.0",
          ext_modules=[Extension("spam", ["spam.c"])])

Build C API source
~~~~~~~~~~~~~~~~~~

.. code-block:: console

    $ python setup.py build
    $ python setup.py install

Run the C module
~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> import spam
    >>> spam.__doc__
    'Example of Module'
    >>> spam.spam
    <type 'spam.Spam'>

PyObject with Member and Methods
--------------------------------

C API source
~~~~~~~~~~~~


.. code-block:: c

    #include <Python.h>
    #include <structmember.h>

    typedef struct {
        PyObject_HEAD
        PyObject *hello;
        PyObject *world;
        int spam_id;
    } spamObj;

    static void
    spamdealloc(spamObj *self)
    {
        Py_XDECREF(self->hello);
        Py_XDECREF(self->world);
        self->ob_type
            ->tp_free((PyObject*)self);
    }

    /* __new__ */
    static PyObject *
    spamNew(PyTypeObject *type, PyObject *args, PyObject *kwds)
    {
        spamObj *self = NULL;

        self = (spamObj *)
               type->tp_alloc(type, 0);
        if (self == NULL) {
            goto END; 
        } 
        /* alloc str to hello */
        self->hello = 
            PyString_FromString("");
        if (self->hello == NULL)
        {
            Py_XDECREF(self);
            self = NULL;
            goto END;
        }
        /* alloc str to world */
        self->world = 
            PyString_FromString("");
        if (self->world == NULL)
        {
            Py_XDECREF(self);
            self = NULL;
            goto END;
        }
        self->spam_id = 0;
    END:
        return (PyObject *)self;
    }

    /* __init__ */
    static int 
    spamInit(spamObj *self, PyObject *args, PyObject *kwds)
    {
        int ret = -1;
        PyObject *hello=NULL, 
                 *world=NULL, 
                 *tmp=NULL;

        static char *kwlist[] = {
            "hello", 
            "world", 
            "spam_id", NULL};

        /* parse input arguments */
        if (! PyArg_ParseTupleAndKeywords(
              args, kwds, 
              "|OOi", 
              kwlist, 
              &hello, &world, 
              &self->spam_id)) {
            goto END;
        }
        /* set attr hello */
        if (hello) {
            tmp = self->hello;
            Py_INCREF(hello);
            self->hello = hello;
            Py_XDECREF(tmp);
        }
        /* set attr world */
        if (world) {
            tmp = self->world;
            Py_INCREF(world);
            self->world = world;
            Py_XDECREF(tmp);
        }
        ret = 0;
    END:
        return ret;
    }

    static long 
    fib(long n) {
        if (n<=2) {
            return 1;
        }
        return fib(n-1)+fib(n-2);
    }

    static PyObject *
    spamFib(spamObj *self, PyObject *args)
    {
        PyObject  *ret = NULL;
        long arg = 0;

        if (!PyArg_ParseTuple(args, "i", &arg)) {
            goto END;
        }
        ret = PyInt_FromLong(fib(arg)); 
    END:
        return ret;
    }

    //ref: python doc
    static PyMemberDef spam_members[] = {
        /* spameObj.hello*/
        {"hello",                   //name
         T_OBJECT_EX,               //type
         offsetof(spamObj, hello),  //offset 
         0,                         //flags
         "spam hello"},             //doc
        /* spamObj.world*/
        {"world", 
         T_OBJECT_EX,
         offsetof(spamObj, world), 
         0,
         "spam world"},
        /* spamObj.spam_id*/
        {"spam_id", 
         T_INT, 
         offsetof(spamObj, spam_id), 
         0,
         "spam id"},
        /* Sentiel */
        {NULL}
    };

    static PyMethodDef spam_methods[] = {
        /* fib */
        {"spam_fib", 
         (PyCFunction)spamFib, 
         METH_VARARGS,
         "Calculate fib number"},
        /* Sentiel */
        {NULL}
    };

    static PyMethodDef module_methods[] = {
        {NULL}  /* Sentinel */
    };

    static PyTypeObject spamKlass = {
        PyObject_HEAD_INIT(NULL)
        0,                               //ob_size
        "spam.spamKlass",                //tp_name
        sizeof(spamObj),                 //tp_basicsize
        0,                               //tp_itemsize
        (destructor) spamdealloc,        //tp_dealloc
        0,                               //tp_print
        0,                               //tp_getattr
        0,                               //tp_setattr
        0,                               //tp_compare
        0,                               //tp_repr
        0,                               //tp_as_number
        0,                               //tp_as_sequence
        0,                               //tp_as_mapping
        0,                               //tp_hash 
        0,                               //tp_call
        0,                               //tp_str
        0,                               //tp_getattro
        0,                               //tp_setattro
        0,                               //tp_as_buffer
        Py_TPFLAGS_DEFAULT | 
        Py_TPFLAGS_BASETYPE,             //tp_flags
        "spamKlass objects",             //tp_doc 
        0,                               //tp_traverse
        0,                               //tp_clear
        0,                               //tp_richcompare
        0,                               //tp_weaklistoffset
        0,                               //tp_iter
        0,                               //tp_iternext
        spam_methods,                    //tp_methods
        spam_members,                    //tp_members
        0,                               //tp_getset
        0,                               //tp_base
        0,                               //tp_dict
        0,                               //tp_descr_get
        0,                               //tp_descr_set
        0,                               //tp_dictoffset
        (initproc)spamInit,              //tp_init
        0,                               //tp_alloc
        spamNew,                         //tp_new
    };

    /* declarations for DLL import */
    #ifndef PyMODINIT_FUNC 
    #define PyMODINIT_FUNC void
    #endif

    PyMODINIT_FUNC
    initspam(void)
    {
        PyObject* m;

        if (PyType_Ready(&spamKlass) < 0) {
            goto END;
        }

        m = Py_InitModule3(
          "spam",         // Mod name 
          module_methods, // Mod methods
          "Spam Module"); // Mod doc  

        if (m == NULL) {
            goto END;
        }
        Py_INCREF(&spamKlass);
        PyModule_AddObject(
          m,                           // Module    
          "SpamKlass",                 // Class Name
          (PyObject *) &spamKlass);    // Class
    END:
        return;
    }

Compare performance with pure Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> import spam
    >>> o = spam.SpamKlass()
    >>> def profile(func):
    ...   def wrapper(*args, **kwargs):
    ...     s = time.time()
    ...     ret = func(*args, **kwargs)
    ...     e = time.time()
    ...     print e-s
    ...   return wrapper
    ...
    >>> def fib(n):
    ...   if n <= 2:
    ...     return n
    ...   return fib(n-1)+fib(n-2)
    ... 
    >>> @profile
    ... def cfib(n):
    ...   o.spam_fib(n)
    ...
    >>> @profile
    ... def pyfib(n):
    ...   fib(n)
    ...
    >>> cfib(30)
    0.0106310844421
    >>> pyfib(30)
    0.399799108505
