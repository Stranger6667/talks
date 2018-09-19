### @color[orange](Pytest)

#### A Python testing framework

---
### Pytest overview

- @color[black](Running tests)
- @color[black](Fixtures)
- @color[black](Parametrization)
- @color[black](Marks)
- @color[black](Plugins)

---
### Unittest

```python
import unittest

def something():
    return 42

class TestSomething(unittest.TestCase):

    def test_success(self):
        self.assertEqual(something(), 42)

    def test_failure(self):
        self.assertEqual(something(), 7)

if __name__ == '__main__':
    unittest.main()
```

---
### Pytest
```python

def something():
    return 42


def test_success():
    assert something() == 42


def test_failure():
    assert something() == 7
```

---
### Command line usage

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
>       assert something() == 7
E       assert 42 == 7
E        +  where 42 = something()

pytest_example.py:12: AssertionError
============================== 1 failed, 1 passed in 0.04 seconds ===============================
```

Pytest can run your unittest tests as well

---
### Command line usage

@size[20px](```-k``` for selecting/deselecting a subset of tests)

```
$ pytest -k test_s pytest_example.py
$ pytest -k not test_s pytest_example.py
```

@size[20px](It will select/deselect all tests that contains ```test_s``` in the name)

---
### Command line usage

@size[20px](```--ignore``` for ignoring some directories / files completely)

```
$ pytest --ignore=python25_tests.py pytest_example.py
```

@size[20px](It will completely ignore ```python25_tests.py``` file)

---
### Fixtures

Flask example

```python
from app import create_flask_app
import pytest


@pytest.fixture
def app():
    instance = create_flask_app("settings.TestSettings")
    with instance.app_context():
        yield instance 


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
```

---
### Fixtures

Usage in tests

```python
def test_something(client):
    assert client.get('/').data == 'Your index content'
```

---
### Fixtures

You could define start-up and tear-down logic using `yield`

```python
import pytest
from app import models


@pytest.fixture
def db_setup(app):
    models.db.create_all(app=app)

    yield models.db

    models.db.drop_all(app=app)
```

---
### Fixtures

You can list all available fixtures with `--fixtures`
```bash
$  pytest --fixtures 
====================================== test session starts =======================================
platform darwin -- Python 3.6.5, pytest-3.8.0, py-1.6.0, pluggy-0.7.1
rootdir: /Users/dmitrydygalo/PycharmProjects/talks/articles/pytest-cheat-sheet/examples, inifile:
collected 0 items                                                                                
cache
    Return a cache object that can persist state between testing sessions.
    
    cache.get(key, default)
    cache.set(key, value)
... 
```

---
### Parametrization

Tests that use `app` will be executed for each app parameter

```python
from app import create_flask_app
import pytest


@pytest.fixture(params=["settings.Setup1", "settings.Setup2"])
def app(request):
    instance = create_flask_app(request.param)
    with instance.app_context():
        yield instance
```

---
### Parametrization

```python
import pytest


def twice(value):
    return value * 2


@pytest.mark.parametrize('value, expected', (
    (1, 2),
    (3, 6),
    (4, 8),
))
def test_twice(value, expected):
    assert twice(value) == expected
```

---
### Marks

Skip slow tests with a custom mark
```python
import pytest

@pytest.mark.slow
def test_cli():
    ...
```

---
### Marks

Skip slow tests with a custom mark

```bash
pytest -m "not slow"  mark_example.py
====================================== test session starts =======================================
platform darwin -- Python 3.6.5, pytest-3.8.0, py-1.6.0, pluggy-0.7.1
rootdir: /Users/dmitrydygalo/PycharmProjects/talks/articles/pytest-cheat-sheet/examples, inifile:
collected 1 item / 1 deselected                                                                  

================================== 1 deselected in 0.00 seconds ==================================
```

---
### Built-in markers

Skip if some condition is met

```python
import sys
import pytest


@pytest.mark.skipif(sys.version_info[0] == 2, reason="Python 2 only test")
def test_something():
    ...
```

---
### Plugins

There are a lot of useful plugins:
- pytest-factoryboy
- pytest-django
- pytest-flask
- pytest-splinter
- pytest-qt
- pytest-asyncio

---
# Thank you

---
### Pytest-factoryboy

```python
class User(Base):
    id = Column(Integer(), primary_key=True)
    name = Column(Text())


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = session   # the SQLAlchemy session object

    id = factory.Sequence(lambda n: n)
    name = "John Doe"
```

---
### Pytest-factoryboy

```python
from pytest_factoryboy import register


@register
class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    ...
```

---
### Pytest-factoryboy

```python
def test_model_fixture(user):
    assert user.name == 'John Doe'


def test_factory_fixture(user_factory):
    assert user_factory().name == 'John Doe'
```
