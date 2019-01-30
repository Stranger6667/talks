### Automated testing in Python

---
### Overview

- Introduction. Purpose & types of automated testing
- `unittest` framework. Core definitions & patterns
- Pytest
- Usage examples

---
### Purpose of testing

### Helps to verify your assumptions about a software product

---
### Common types of testing

- Unit
- Integration
- Functional
- Acceptance

Note:
- smallest unit of functionality
- multiple units together
- work with particular feature
- usually features from user point of view  

---
### Unittest framework

---
### Code example

```python
# project.py
def add(x, y):
    return x + y

def sub(x, y):
    return x - y
```

+++
### Test cases

```python
# test_add.py
import unittest

from project import add


class TestIntegers(unittest.TestCase):

    def test_success(self):
        self.assertEqual(add(2, 2), 4)

    def test_failure(self):
        # Illustrates test failure
        self.assertEqual(add(2, 3), 6)


if __name__ == '__main__':
    unittest.main()
```

Note:
- test methods names start with `test_`
- to verify your assumption you run `assert*` method
- `main()` is for CLI

---
### How to run tests

```bash
$ python test_add.py
```

+++
### How to run tests

```bash
$ python -m unittest test_add test_sub
$ python -m unittest test_add.TestIntegers
$ python -m unittest test_add.TestIntegers.test_success
```

+++
### Test discovery

```bash
$ python -m unittest
```

#### Will look for tests in the current directory

---
### Test fixtures

```python
import sqlite3
import unittest

class TestIntegers(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect('test.db')
        self.cursor = self.connection.cursor()

    def test_sql(self):
        self.cursor.execute("SELECT 2 + 2")
        result = self.cursor.fetchone()[0]
        self.assertEqual(result, 4)

    def tearDown(self):
        self.cursor.close()
        self.connection.close()
```

---
### Usual test's structure

- set up
- execute
- assert
- tear down

+++
### Usual test's structure

#### Test cases

- set up
- run all tests in the test case
- tear down

---
### Common assertions

- assertEqual
- assertNotEqual
- assertLess
- assertGreater
- ... # a lot of them

##### https://docs.python.org/3/library/unittest.html

---
### How to organize a test suite

- classes
- modules
- packages

---
### Unittest summary

- test case
- test suite
- test fixture
- test runner

---
### Pytest

#### Python testing framework

---
---
### Unittest

```python
...
class TestIntegers(unittest.TestCase):

    def test_success(self):
        self.assertEqual(add(2, 2), 4)

    def test_failure(self):
        # Illustrates test failure
        self.assertEqual(add(2, 3), 6)

if __name__ == '__main__':
    unittest.main()
```

---
### Pytest
```python
from project import add

def test_success():
    assert add(2, 2) == 4

def test_failure():
    assert add(2, 3) == 6
```

---
### How to run tests with pytest
```bash
$ pytest pytest_example.py
====================================== test session starts ======================================
platform darwin -- Python 3.6.5, pytest-3.8.0, py-1.6.0, pluggy-0.7.1
rootdir: /Users/dmitrydygalo/PycharmProjects/talks/articles/pytest-cheat-sheet/examples, inifile:
collected 2 items                                                                              

pytest_example.py .F                                                                      [100%]

=========================================== FAILURES ============================================
_________________________________________ test_failure __________________________________________

    def test_failure():
>       assert add(2, 3) == 6
E       assert 5 == 6
E        +  where 5 = add(2, 3)

pytest_example.py:12: AssertionError
============================== 1 failed, 1 passed in 0.04 seconds ===============================
```

Pytest can run your unittest tests as well

---
### Fixtures

```python
class TestIntegers(unittest.TestCase):

    def setUp(self):
        self.connection = sqlite3.connect('test.db')
        self.cursor = self.connection.cursor()

    def test_sql(self):
        self.cursor.execute("SELECT 2 + 2")
        result = self.cursor.fetchone()[0]
        self.assertEqual(result, 4)

    def tearDown(self):
        self.cursor.close()
        self.connection.close()
```

+++
### Fixtures

```python
import sqlite3

import pytest

@pytest.fixture()
def cursor():
    connection = sqlite3.connect('test.db')
    cursor = connection.cursor()
    yield cursor
    cursor.close()
    connection.close()
    
```

+++
### Fixtures

```python
def test_sql(cursor):
    cursor.execute("SELECT 2 + 2")
    result = cursor.fetchone()[0]
    assert result == 4
```

---
### Parametrization

```python
@pytest.mark.parametrize("x, y, expected", (
    (2, 2, 4),
    (2, 3, 6),
))
def test_add(x, y, expected):
    assert add(x, y) == expected
```

---
### Usage examples

- Selenium
- Report to HTML / XML / Issue tracker

#### There are a lot of plugins for pytest 
```python
def test_example(selenium):
    selenium.get('http://www.example.com')
```

#### Selenium