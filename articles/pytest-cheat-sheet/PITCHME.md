### @color[orange](Pytest)

#### A Python testing framework

---
### What pytest is
15 sec 

---
@transition[none]
@snap[north]
<h3>Unittest</h3>
@snapend
1 min

code example
```python
import unittest


def something():
    return [42]


class TestSomething(unittest.TestCase):

    def test_feature(self):
        self.assertEqual(something(), [42])

    def test_failure(self):
        self.assertEqual(something(), [7])


if __name__ == '__main__':
    unittest.main()
```

```python

def something():
    return [42]


def test_feature():
    assert something() == 42
```


```bash
$ pytest -v test_something.py
======================================================================================================================== test session starts ========================================================================================================================
platform darwin -- Python 3.6.5, pytest-3.6.1, py-1.5.3, pluggy-0.6.0 -- /Library/Frameworks/Python.framework/Versions/3.6/bin/python3.6
cachedir: ../../.pytest_cache
rootdir: /Users/dmitrydygalo, inifile:
plugins: celery-4.1.0
collected 2 items                                                                                                                                                                                                                                                   

../../Library/Preferences/PyCharm2018.2/scratches/scratch_17.py::test_feature PASSED                                                                                                                                                                          [ 50%]
../../Library/Preferences/PyCharm2018.2/scratches/scratch_17.py::test_failure FAILED                                                                                                                                                                          [100%]

============================================================================================================================= FAILURES ==============================================================================================================================
___________________________________________________________________________________________________________________________ test_failure ____________________________________________________________________________________________________________________________

    def test_failure():
>       assert something() == [7]
E       assert [42] == [7]
E         At index 0 diff: 42 != 7
E         Full diff:
E         - [42]
E         + [7]

../../Library/Preferences/PyCharm2018.2/scratches/scratch_17.py:12: AssertionError
================================================================================================================ 1 failed, 1 passed in 0.06 seconds =================================================================================================================

```


CMD example
CMD output with failures to demonstrate reporting



# Test discovery
30 sec

-k for select something and exclude another
--ignore for some incompatible code

```bash
 pytest -k test_feature -v /Users/dmitrydygalo/Library/Preferences/PyCharm2018.2/scratches/scratch_17.py
======================================================================================================================== test session starts ========================================================================================================================
platform darwin -- Python 3.6.5, pytest-3.6.1, py-1.5.3, pluggy-0.6.0 -- /Library/Frameworks/Python.framework/Versions/3.6/bin/python3.6
cachedir: ../../.pytest_cache
rootdir: /Users/dmitrydygalo, inifile:
plugins: celery-4.1.0
collected 2 items / 1 deselected                                                                                                                                                                                                                                    

../../Library/Preferences/PyCharm2018.2/scratches/scratch_17.py::test_feature PASSED                                                                                                                                                                          [100%]

============================================================================================================== 1 passed, 1 deselected in 0.01 seconds ===============================================================================================================
```

```bash
pytest --ignore tests/python2_tests tests
```

# Fixtures
1 min

Simple example + usage in tests
```python
from app import create_flask_app
import pytest


@pytest.fixture
def app():
    instance = create_flask_app()
    with instance.app_context():
        yield instance 


@pytest.fixture
def client(app):
    return app.test_client()


def test_something(client):
    assert client.get('/').data == 'Your index content'
```


Session-scope fixtures. Teardown logic for fixtures. Mock for example?

```python
import pytest
from app import models


@pytest.fixture(scope="session")
def db_setup(app):
    models.db.create_all(app=app)

    yield models.db

    models.db.drop_all(app=app)
```

CMD + output with --fixtures listing
```bash
$ pytest --fixtures
======================================================================================================================== test session starts ========================================================================================================================
platform darwin -- Python 3.6.5, pytest-3.6.1, py-1.5.3, pluggy-0.6.0
rootdir: /Users/dmitrydygalo/PycharmProjects/talks, inifile:
plugins: celery-4.1.0
collected 0 items                                                                                                                                                                                                                                                   
<fixtures list>
```

# Parametrization
30 sec

In fixtures. code example
```python

```
On functions. Code example + output

# Marks
30 sec

Skipif. Different platforms / Pythons + output
Xfail. Output

# Plugin
1 minute
- pytest-django. client + assert queries number
- pytest-factoryboy. Model + factory + test.
- pytest-flask. `options` mark 
- pytest-selenium. selenium.get() example + CMD option with driver.



plan:
1. What py.test is. General idea. 15 sec 
2. Small example of test vs unittest. plain asserts + example of output. unit tests could be run by py.test. 1 min 
3. Test discovery. -k / --ignore. example for python 2 / 3 incompat. 30 sec
4. Fixtures. Simple definition. Different scopes. Teardown logic with yield. 1 min  
5. Parametrization. 30 sec
6. Marks. Skipif / xfail. 30 sec
7. Plugins. 30 sec