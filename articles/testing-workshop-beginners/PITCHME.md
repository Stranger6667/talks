# Automated testing in Python

---
### Overview

- Introduction. Purpose and types of automated testing
- **`unittest`** framework. Core definitions and patterns
- Pytest
- Usage examples

---
### Purpose of testing

#### Helps to verify your assumptions about a software product

---
@transition[none]
@snap[north]
#### Common types of testing
@snapend

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
@transition[none]
@snap[north]
### Code example
@snapend

```python
def add(x, y):
    return x + y

def sub(x, y):
    return x - y
```
@[1-2]
@[4-5]

##### **`project.py`**

+++
@transition[none]
@snap[north]
### Test cases
@snapend

```python
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

@[1] Import unittest
@[3] Import you code
@[5] Create a subclass
@[7-8] Define your tests 
@[10-12] Define your tests 
@[14-15] To run tests
 
##### **`test_add.py`**

Note:
- test methods names start with `test_`
- to verify your assumption you run `assert*` method
- `main()` is for CLI

---
@transition[none]
@snap[north]
### How to run tests
@snapend

```
$ python test_add.py
```

+++
@transition[none]
@snap[north]
### How to run tests
@snapend

```
$ python -m unittest test_add test_sub
$ python -m unittest test_add.TestIntegers
$ python -m unittest test_add.TestIntegers.test_success
```

+++
@transition[none]
@snap[north]
### Test discovery
@snapend

```
$ python -m unittest
```

#### Will look for tests in the current directory

---
@transition[none]
@snap[north]
### Test fixtures
@snapend

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

@[5-7]
@[9-12]
@[14-16]

##### **`test_database.py``**

---
### Usual test structure

- set up
- execute
- assert
- tear down

+++
### Usual test structure

- set up
- run all tests in the test case
- tear down

---
@transition[none]
@snap[north]
#### Common assertions
@snapend

- assertEqual
- assertNotEqual
- assertLess
- assertGreater
- ...

---
@transition[none]
@snap[north]
### Documentation
@snapend

### https://docs.python.org/3/library/unittest.html

---
@transition[none]
@snap[north]
#### How to organize a test suite
@snapend

- classes
- modules
- packages

---
@transition[none]
@snap[north]
### Unittest summary
@snapend

- test case
- test suite
- test fixture
- test runner

Note:
- Individual unit of testing
- Test suite - a collection of test cases or test suites
- A test fixture represents the preparation needed to perform one or more tests, and any associate cleanup actions
- Runs tests, provides reports

---
### Pytest

#### Python testing framework

---
@transition[none]
@snap[north]
### Unittest
@snapend

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
@transition[none]
@snap[north]
### Pytest
@snapend

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
@transition[none]
@snap[north]
### Fixtures
@snapend

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
@transition[none]
@snap[north]
### Fixtures
@snapend

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

@[5-6]
@[7-8]
@[9]
@[10-11]

+++
@transition[none]
@snap[north]
### Fixtures
@snapend

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
- Graphic interfaces
- API testing
- Report to HTML / XML / Issue tracker
 
---
### Selenium

```python
def test_example(selenium):
    selenium.get('http://www.example.com')
```

---
### Graphic interfaces

```python
def test_hello(qtbot):
    widget = HelloWidget()
    qtbot.addWidget(widget)

    # click in the Greet button and make sure it updates the appropriate label
    qtbot.mouseClick(window.button_greet, QtCore.Qt.LeftButton)

    assert window.greet_label.text() == 'Hello!'
```