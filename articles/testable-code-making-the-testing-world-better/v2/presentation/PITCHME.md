### @color[orange](Testable code)

#### Making the testing world better

---
### Who am I

- @color[black](Tech Lead at kiwi.com)
- @color[black](Live in Prague, Czech Republic)
- @color[black](Love Python & open-source)

Note:
Hello everyone, my name is Dmitry Dygalo and I am a technical team lead at kiwi.com. 
I live in Prague and I like to build tools in Python. Also I like to contribute to open-source projects.
Currently, I’m working on splitting a big legacy monolith into small and handy microservices. 
This kind of activity often goes together with refactoring and fixing old problems. 

---
### Let's make things right (again)!

<img src="articles/testable-code-making-the-testing-world-better/v1/presentation/assets/img/lets-make-right.jpg" alt="Make right" width="600px"/>

Note:
If we are starting with a fresh new project, then why not do things right (again?) at the beginning?

---
### Important aspects of testing

@ul
- @color[black](Isolation)
- @color[black](Independence)
- @color[black](Repeatability)
- @color[black](Speed)
@ulend

Note: 
- Tests should not interfere with each other
- You should be able to run any subset of your tests in any order
- You should be able to easily reproduce any test failure
- You should be able to get these results fast

These principles apply to different testing levels.
For unittests when you’re testing small, independent units of your code and as well for integration tests.

---
@transition[none]
@snap[north]
<h3>Global variables</h3>
@snapend

```python
import logging

logger = logging.getLogger(__name__)
```

+++
@transition[none]
@snap[north]
<h3>Global variables</h3>
@snapend

```python
# logging/__init__.py
root = RootLogger(WARNING)
Logger.root = root
Logger.manager = Manager(Logger.root)

def getLogger(name=None):
    if name:
        return Logger.manager.getLogger(name)
    else:
        return root
```

---
### Imports in Python

```python
module = create_module_object(name)
code = get_module_code(name)
exec(code, module.__dict__)
sys.modules[module.__spec__.name] = module
```

More: 

https://github.com/python/cpython/blob/master/Lib/importlib/_bootstrap.py

Note:
Next time Python’s import machinery will look at `sys.modules` first.
If you want to invalidate cache you need to remove a key from `sys.modules`.

---
### Testing?

Note:
If some module is required in two different tests, then it will be executed in a context of the first test and then it will be taken from cache in the second test, unless it is not reloaded.
It could lead to various issues if the second test module requires different context to be tested.

---
### Example

```python

```

---
### Test example


---
### Details

# identity map explanation + code example

---
### Thread-local session

---
### Result

- Identity map is modified
- Changes are committed to the DB

---
### Monkey-patching

# real example from the codebase

---
### It could fix some symptoms, but it doesn't fix the problem

<img src="articles/testable-code-making-the-testing-world-better/v1/presentation/assets/img/fix-problem.jpg" alt="Fix problem" width="600px"/>

Note:
In large projects, it could lead to monkey patching a significant amount of different modules.

---
### Let's make it better

Note:
The global state in the previous examples is hardly predictable. Let’s change it and make it manageable.
The first step is to take control when the object is initialised. 
We want to initialise it only when we need it; just in the desired context.

---
@transition[none]
@snap[north]
<h3>Deferred initialization and application context</h3>
@snapend

#### Flask-SQLAlchemy

# Python example

Note:
Flask has a beautiful way of solving this problem — init_app pattern. 
It allows you to isolate some global state in an object and control when to initialise it. 
Also, it used to register some teardown logic for this global object.

+++
@transition[none]
@snap[north]
<h3>After</h3>
@snapend

##### `Flask-SQLAlchemy` 

```python
# database.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# app.py
from flask import Flask

application = App(__name__)

from .database import db

db.init_app(application)

# conftest.py
from .app import application
import database


@pytest.fixture(scope="session")
def db():
    # Create extensions, tables, etc
    yield database.db
    # Drop tables, extensions, etc


@pytest.fixture(autouse=True)
def session(db):
    db.session.begin_nested()
    yield db.session
    db.session.rollback()
```

@[1-13](Database & Application)
@[15-31])(New shiny fixtures)

Note:
This is how it could be changed with `Flask-SQLAlchemy` extension.
Now the database is initialised only when the application initialises — we put the DB into application context.

+++
@transition[none]
@snap[north]
<h3>Benefits</h3>
@snapend

@ul
- @color[black](Manageable DB initialization)
- @color[black](No monkeypatching)
@ulend

Note:
As a consequence, we don’t have to initialise another database connection in tests and make monkey patches.
We’re managing this global state.

---
@transition[none]
@snap[north]
<h3>Application factory</h3>
@snapend

```python
# app.py
def create_app(settings_object, **kwargs):
    flask_app = Flask(__name__)
    flask_app.config.from_object(settings_object)
    flask_app.config.update(**kwargs)

    from .database import db

    db.init_app(flask_app)
    db.app = flask_app

    return flask_app

# conftest.py
from app import create_app


@pytest.fixture(scope="session")
def app():
    return create_app("app.settings.TestSettings")


@pytest.fixture(scope="session")
def db(app):
    # Create extensions, tables, etc
    yield database.db
    # Drop tables, extensions, etc
```

@[1-12](Application factory)
@[13-26])(New shiny fixtures)

Note:
However, application is still global, and it initializes on import. 
If we didn’t initialise the DB before running the tests, it wouldn’t work. 
To address this problem the application factory pattern exists.
The basic idea is to isolate the application instance creation in a separate function.

+++
@transition[none]
@snap[north]
<h3>Application factory</h3>
@snapend

@ul
- @color[black](Isolation. An application instance is created after the test session starts)
- @color[black](Flexibility. Parametrise with different setting)
@ulend

Note:
- Isolate the side-effects of creating an application on the module-level. 
- Flexibility — multiple apps and/ore different settings. It’s available as a fixture, which provides more flexibility (e.g., parametrization)

---
@transition[none]
@snap[north]
<h3>Dependency injection</h3>
@snapend

+++
@transition[none]
@snap[north]
<h3>Dependency injection</h3>
@snapend

# Flask example + Flask-SQLAlchemy
Note:
There is another technique that was used in the previous examples but wasn’t mentioned explicitly. Dependency injection.

+++
@transition[none]
@snap[north]
<h3>Dependency injection</h3>
@snapend

# Redis-py connection pool + tests
+++
@transition[none]
@snap[north]
<h3>Dependency injection</h3>
@snapend

@ul
- @color[black](Decoupling execution from implementation)
- @color[black](Easier to mock heavy dependencies)
@ulend

Note:
Applying this approach allows you to decouple the execution of a task from its implementation.
Now, you can pass any engine you want to the airplane and test its logic with different engines, or mock your engine to see if it’s too heavy for an ordinary test.
For example, you could isolate some hard-to-test logic (e.g., a 3rd party service or some heavy computations) in this “dependency” and pass a mock object in tests instead of the real one.
Flask allows you to write isolated extensions with ease, in pytest you can reuse and parametrize fixtures in tests.

---
# Multiple inheritance

---
@transition[none]
@snap[north]
<h3>Data & logic separation</h3>
@snapend

Note:
When you’re writing tests, usually you use some values as an input for your testing logic, and you expect some other values to be an output of this logic

+++
@transition[none]
@snap[north]
<h3>Data & logic separation</h3>
@snapend

```python
def test_something():
    assert something('a', 'b') == 'c'
```

Note:
But when you hardcode them inside the testing code, it makes it less extendable. 
If you keep test data separate from the test logic, it will make modifications much more manageable. 
Dependency injection’s back in the game!

+++
@transition[none]
@snap[north]
<h3>Data & logic separation</h3>
@snapend

```python
@pytest.mark.parametrize(
    'first, second, expected', 
    (
        ('a', 'b', 'c'), 
        ('b', 'a', 'd')
    )
)
def test_something(first, second, expected):
    assert something(first, second) == expected
```

Note:
Here you have pytest parametrisation and you can easily add new test cases.

+++
@transition[none]
@snap[north]
<h3>Data & logic separation</h3>
@snapend

@ul
- @color[black](Easier to add new test cases)
- @color[black](Easier to refactor tests)
@ulend

Note:
It is especially helpful if you have an extensive test suite — it can help you see similarities in your tests and 
refactor them or build some reusable tools, that might help you in the future.

---
@transition[none]
@snap[north]
<h3>More factories</h3>
@snapend

##### `factoryboy`

```python
class User(Base):
    id = Column(Integer(), primary_key=True)
    name = Column(Unicode(20))


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = session   # the SQLAlchemy session object

    id = factory.Sequence(lambda n: n)
    name = 'John Doe'
```

Note:
But what if the object you’re testing is more complicated than a string? SQLAlchemy model for example. 
You could create them manually in a separate fixture, or you could use something like factory-boy.

+++
@transition[none]
@snap[north]
<h3>More factories</h3>
@snapend

##### `factoryboy`

```python
>>> UserFactory()
<User: User 1>
>>> session.query(User).all()
[<User: User 1>]
```

+++
@transition[none]
@snap[north]
<h3>More factories</h3>
@snapend

##### `pytest-factoryboy`

```python
from pytest_factoryboy import register


@register
class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    ...
```

Note:
Factory boy is very well integrated with py.test the with absolutely gorgeous pytest-factoryboy. 
Just register your factories and make sure that they’re imported in your test suite (in the root conftest.py, for example):

+++
@transition[none]
@snap[north]
<h3>More factories</h3>
@snapend

##### `pytest-factoryboy`

```python
def test_model_fixture(user):
    assert user.name == 'John Doe'


def test_factory_fixture(user_factory):
    assert user_factory().name == 'John Doe'
```

Note:
and now you magically have user and user_factory fixtures.
The user fixture corresponds to a simple factory call without arguments.

+++
@transition[none]
@snap[north]
<h3>More factories</h3>
@snapend

Check out `pytest-factoryboy`

https://github.com/pytest-dev/pytest-factoryboy

Note:
pytest-factoryboy provides a lot of different features that are worth checking out.

---
> Testing shows the presence, not the absence of bugs.

##### Edsger W. Dijkstra

Note:
And the most important thing is the mindset - you should treat tests & testability as first-class citizens of your development process. 

---

### Thank you

- https://github.com/Stranger6667
- https://twitter.com/Stranger6667
- https://code.kiwi.com/testable-code-making-the-testing-world-better-76b6461c630