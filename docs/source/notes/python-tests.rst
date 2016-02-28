======================
Python test cheatsheet
======================

A simple Python unittest
------------------------

.. code-block:: python

    # python unittet only run the function with prefix "test"
    >>> import unittest
    >>> class TestFoo(unittest.TestCase):
    ...     def test_foo(self):
    ...             self.assertTrue(True)
    ...     def fun_not_run(self):
    ...             print "no run"
    ... 
    >>> unittest.main()
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.000s

    OK
    >>> import unittest
    >>> class TestFail(unittest.TestCase):
    ...     def test_false(self):
    ...             self.assertTrue(False)
    ... 
    >>> unittest.main()
    F
    ======================================================================
    FAIL: test_false (__main__.TestFail)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "<stdin>", line 3, in test_false
    AssertionError: False is not true

    ----------------------------------------------------------------------
    Ran 1 test in 0.000s

    FAILED (failures=1)


Python unittest setup & teardown hierarchy
------------------------------------------

.. code-block:: python

    import unittest

    def fib(n):
        return 1 if n<=2 else fib(n-1)+fib(n-2)

    def setUpModule():
            print "setup module" 
    def tearDownModule():
            print "teardown module"

    class TestFib(unittest.TestCase):

        def setUp(self):
            print "setUp"
            self.n = 10
        def tearDown(self):
            print "tearDown"
            del self.n
        @classmethod
        def setUpClass(cls):
            print "setUpClass"
        @classmethod
        def tearDownClass(cls):
            print "tearDownClass"
        def test_fib_assert_equal(self):
            self.assertEqual(fib(self.n), 55)
        def test_fib_assert_true(self):
            self.assertTrue(fib(self.n) == 55)

    if __name__ == "__main__":
        unittest.main()

output:

.. code-block:: console 

    $ python test.py
    setup module
    setUpClass
    setUp
    tearDown
    .setUp
    tearDown
    .tearDownClass
    teardown module

    ----------------------------------------------------------------------
    Ran 2 tests in 0.000s

    OK

Different module of setUp & tearDown hierarchy
----------------------------------------------

.. code-block:: python

    # test_module.py
    import unittest

    class TestFoo(unittest.TestCase):
        @classmethod
        def setUpClass(self):
            print "foo setUpClass"
        @classmethod
        def tearDownClass(self):
            print "foo tearDownClass"
        def setUp(self):
            print "foo setUp"
        def tearDown(self):
            print "foo tearDown"
        def test_foo(self):
            self.assertTrue(True)

    class TestBar(unittest.TestCase):
        def setUp(self):
            print "bar setUp"
        def tearDown(self):
            print "bar tearDown"
        def test_bar(self):
            self.assertTrue(True)

    # test.py
    from test_module import TestFoo
    from test_module import TestBar
    import test_module
    import unittest

    def setUpModule():
        print "setUpModule"

    def tearDownModule():
        print "tearDownModule"


    if __name__ == "__main__":
        test_module.setUpModule = setUpModule
        test_module.tearDownModule = tearDownModule
        suite1 = unittest.TestLoader().loadTestsFromTestCase(TestFoo)
        suite2 = unittest.TestLoader().loadTestsFromTestCase(TestBar)
        suite = unittest.TestSuite([suite1,suite2])
        unittest.TextTestRunner().run(suite)


output:

.. code-block:: console

    $ python test.py
    setUpModule
    foo setUpClass
    foo setUp
    foo tearDown
    .foo tearDownClass
    bar setUp
    bar tearDown
    .tearDownModule

    ----------------------------------------------------------------------
    Ran 2 tests in 0.000s

    OK

Run tests via unittest.TextTestRunner
-------------------------------------

.. code-block:: python

    >>> import unittest  
    >>> class TestFoo(unittest.TestCase):
    ...     def test_foo(self):
    ...         self.assertTrue(True)
    ...     def test_bar(self):
    ...         self.assertFalse(False)  

    >>> suite = unittest.TestLoader().loadTestsFromTestCase(TestFoo)  
    >>> unittest.TextTestRunner(verbosity=2).run(suite)  
    test_bar (__main__.TestFoo) ... ok
    test_foo (__main__.TestFoo) ... ok

    ----------------------------------------------------------------------
    Ran 2 tests in 0.000s

    OK

Test raise exception
--------------------

.. code-block:: python

    >>> import unittest  

    >>> class TestRaiseException(unittest.TestCase):
    ...     def test_raise_except(self):
    ...         with self.assertRaises(SystemError):
    ...             raise SystemError  
    >>> suite_loader = unittest.TestLoader()  
    >>> suite = suite_loader.loadTestsFromTestCase(TestRaiseException)  
    >>> unittest.TextTestRunner().run(suite)  
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.000s

    OK
    >>> class TestRaiseFail(unittest.TestCase):
    ...     def test_raise_fail(self):
    ...         with self.assertRaises(SystemError):
    ...             pass  
    >>> suite = unittest.TestLoader().loadTestsFromTestCase(TestRaiseFail)  
    >>> unittest.TextTestRunner(verbosity=2).run(suite)  
    test_raise_fail (__main__.TestRaiseFail) ... FAIL

    ======================================================================
    FAIL: test_raise_fail (__main__.TestRaiseFail)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "<stdin>", line 4, in test_raise_fail
    AssertionError: SystemError not raised

    ----------------------------------------------------------------------
    Ran 1 test in 0.000s

    FAILED (failures=1)


Pass arguments into a TestCase
------------------------------

.. code-block:: python

    >>> import unittest  
    >>> class TestArg(unittest.TestCase):
    ...     def __init__(self, testname, arg):
    ...         super(TestArg, self).__init__(testname)
    ...         self._arg = arg
    ...     def setUp(self):
    ...         print "setUp:", self._arg
    ...     def test_arg(self):
    ...         print "test_arg:", self._arg
    ...         self.assertTrue(True)  
    ...
    >>> suite = unittest.TestSuite()  
    >>> suite.addTest(TestArg('test_arg', 'foo'))  
    >>> unittest.TextTestRunner(verbosity=2).run(suite)  
    test_arg (__main__.TestArg) ... setUp: foo
    test_arg: foo
    ok

    ----------------------------------------------------------------------
    Ran 1 test in 0.000s

    OK

Group multiple testcases into a suite
-------------------------------------

.. code-block:: python

    >>> import unittest  
    >>> class TestFooBar(unittest.TestCase):
    ...     def test_foo(self):
    ...         self.assertTrue(True)
    ...     def test_bar(self):
    ...         self.assertTrue(True)  
    ...
    >>> class TestHelloWorld(unittest.TestCase):
    ...     def test_hello(self):
    ...         self.assertEqual("Hello", "Hello")
    ...     def test_world(self):
    ...         self.assertEqual("World", "World")  
    ...
    >>> suite_loader = unittest.TestLoader()  
    >>> suite1 = suite_loader.loadTestsFromTestCase(TestFooBar)  
    >>> suite2 = suite_loader.loadTestsFromTestCase(TestHelloWorld)  
    >>> suite = unittest.TestSuite([suite1, suite2])  
    >>> unittest.TextTestRunner(verbosity=2).run(suite)  
    test_bar (__main__.TestFooBar) ... ok
    test_foo (__main__.TestFooBar) ... ok
    test_hello (__main__.TestHelloWorld) ... ok
    test_world (__main__.TestHelloWorld) ... ok

    ----------------------------------------------------------------------
    Ran 4 tests in 0.000s

    OK

Group multiple tests from different TestCase
--------------------------------------------

.. code-block:: python

    >>> import unittest  
    >>> class TestFoo(unittest.TestCase):
    ...     def test_foo(self):
    ...         assert "foo" == "foo"  
    ...
    >>> class TestBar(unittest.TestCase):
    ...     def test_bar(self):
    ...         assert "bar" == "bar"  
    ...
    >>> suite = unittest.TestSuite()  
    >>> suite.addTest(TestFoo('test_foo'))  
    >>> suite.addTest(TestBar('test_bar'))  
    >>> unittest.TextTestRunner(verbosity=2).run(suite)  
    test_foo (__main__.TestFoo) ... ok
    test_bar (__main__.TestBar) ... ok

    ----------------------------------------------------------------------
    Ran 2 tests in 0.001s

    OK

Skip some tests in the TestCase
-------------------------------

.. code-block:: python

    >>> import unittest  
    >>> RUN_FOO = False  
    >>> DONT_RUN_BAR = False  
    >>> class TestSkip(unittest.TestCase):
    ...     def test_always_run(self):
    ...         self.assertTrue(True)
    ...     @unittest.skip("always skip this test")
    ...     def test_always_skip(self):
    ...         raise RuntimeError
    ...     @unittest.skipIf(RUN_FOO == False, "demo skipIf")
    ...     def test_skipif(self):
    ...         raise RuntimeError
    ...     @unittest.skipUnless(DONT_RUN_BAR == True, "demo skipUnless")
    ...     def test_skipunless(self):
    ...         raise RuntimeError  
    ...
    >>> suite = unittest.TestLoader().loadTestsFromTestCase(TestSkip)  
    >>> unittest.TextTestRunner(verbosity=2).run(suite)  
    test_always_run (__main__.TestSkip) ... ok
    test_always_skip (__main__.TestSkip) ... skipped 'always skip this test'
    test_skipif (__main__.TestSkip) ... skipped 'demo skipIf'
    test_skipunless (__main__.TestSkip) ... skipped 'demo skipUnless'

    ----------------------------------------------------------------------
    Ran 4 tests in 0.000s

    OK (skipped=3)

Cross-module variables to Test files
------------------------------------

test_foo.py

.. code-block:: python

    import unittest

    print conf

    class TestFoo(unittest.TestCase):
        def test_foo(self):
            print conf
            
        @unittest.skipIf(conf.isskip==True, "skip test")
        def test_skip(self):
            raise RuntimeError

test_bar.py

.. code-block:: python

    import unittest
    import __builtin__

    if __name__ == "__main__":
        conf = type('TestConf', (object,), {})
        conf.isskip = True

        # make a cross-module variable
        __builtin__.conf = conf
        module = __import__('test_foo')
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(module.TestFoo)
        unittest.TextTestRunner(verbosity=2).run(suite)

output:

.. code-block:: console

    $ python test_bar.py
    <class '__main__.TestConf'>
    test_foo (test_foo.TestFoo) ... <class '__main__.TestConf'>
    ok
    test_skip (test_foo.TestFoo) ... skipped 'skip test'

    ----------------------------------------------------------------------
    Ran 2 tests in 0.000s

    OK (skipped=1)


skip setup & teardown when the test is skipped
-----------------------------------------------

.. code-block:: python

    >>> import unittest
    >>> class TestSkip(unittest.TestCase):
    ...     def setUp(self):
    ...         print "setUp"
    ...     def tearDown(self):
    ...         print "tearDown"
    ...     @unittest.skip("skip this test")
    ...     def test_skip(self):
    ...         raise RuntimeError
    ...     def test_not_skip(self):
    ...         self.assertTrue(True)  
    ...
    >>> suite = unittest.TestLoader().loadTestsFromTestCase(TestSkip)  
    >>> unittest.TextTestRunner(verbosity=2).run(suite)  
    test_not_skip (__main__.TestSkip) ... setUp
    tearDown
    ok
    test_skip (__main__.TestSkip) ... skipped 'skip this test'

    ----------------------------------------------------------------------
    Ran 2 tests in 0.000s

    OK (skipped=1)

Re-using old test code
----------------------

.. code-block:: python

    >>> import unittest
    >>> def old_func_test():
    ...     assert "Hello" == "Hello"                                                                                                                                                                                                      
    ... 
    >>> def old_func_setup():                                                                                                                                                                                                              
    ...     print "setup"
    ... 
    >>> def old_func_teardown():
    ...     print "teardown"                                                                                                                                                                                                               
    ... 
    >>> testcase = unittest.FunctionTestCase(old_func_test,
    ...                                      setUp=old_func_setup,
    ...                                      tearDown=old_func_teardown)
    >>> suite = unittest.TestSuite([testcase])
    >>> unittest.TextTestRunner().run(suite)
    setup
    teardown
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.000s

    OK
    <unittest.runner.TextTestResult run=1 errors=0 failures=0>

Testing your document is right
------------------------------

.. code-block:: python

    """
    This is an example of doctest

    >>> fib(10)
    55
    """

    def fib(n):
    """
    This function calculate fib number.

    example:

    >>> fib(10)
    55
    >>> fib(-1)
    Traceback (most recent call last):
    ...
    ValueError
    """
    if n < 0:
    raise ValueError('')
    return 1 if n<=2 else fib(n-1) + fib(n-2)

    if __name__ == "__main__":
    import doctest
    doctest.testmod()

    # output:
    bash> python demo_doctest.py -v
    Trying:
    fib(10)
    Expecting:
    55
    ok
    Trying:
    fib(10)
    Expecting:
    55
    ok
    Trying:
    fib(-1)
    Expecting:
    Traceback (most recent call last):
    ...
    ValueError
    ok
    2 items passed all tests:
    1 tests in __main__
    2 tests in __main__.fib
    3 tests in 2 items.
    3 passed and 0 failed.
    Test passed.

Re-using doctest to unittest
----------------------------

.. code-block:: python

    import unittest
    import doctest

    """
    This is an example of doctest

    >>> fib(10)
    55
    """

    def fib(n):
        """
        This function calculate fib number.

        example:

        >>> fib(10)
        55
        >>> fib(-1)
        Traceback (most recent call last):
            ...
        ValueError
        """
        if n < 0:
            raise ValueError('')
        return 1 if n<=2 else fib(n-1) + fib(n-2)

    if __name__ == "__main__":
        finder = doctest.DocTestFinder()
        suite = doctest.DocTestSuite(test_finder=finder)
        unittest.TextTestRunner(verbosity=2).run(suite)

output:

.. code-block:: console

    fib (__main__)
    Doctest: __main__.fib ... ok

    ----------------------------------------------------------------------
    Ran 1 test in 0.023s

    OK

Mocking Test
------------

without mock - test will always failed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import unittest
    import os

    class TestFoo(unittest.TestCase):
        def test_foo(self):
            os.remove('!@#$%^~')

    if __name__ == "__main__":
        unittest.main()

output:

.. code-block:: console

    $ python wo_mock_test.py 
    E
    ======================================================================
    ERROR: test_foo (__main__.TestFoo)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "mock_test.py", line 7, in test_foo
        os.remove('!@#$%^~')
    OSError: [Errno 2] No such file or directory: '!@#$%^~'

    ----------------------------------------------------------------------
    Ran 1 test in 0.000s

with mock - substitute real object to fake object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import mock
    import unittest
    import os

    def mock_os_remove(path):
        pass

    class TestFoo(unittest.TestCase):
        @mock.patch('os.remove', mock_os_remove)
        def test_foo(self):
            os.remove('!@#$%^~')

    if __name__ == "__main__":
        unittest.main()

output:

.. code-block:: console

    $ python w_mock_test.py 
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.000s

    OK
