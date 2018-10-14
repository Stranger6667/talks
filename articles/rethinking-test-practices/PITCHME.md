### @color[orange](Rethinking testing practices)

#### Avoid shooting yourself in the foot

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
### Overview

- Testing aspects and goals
- Previous state
- Problems & alternatives
- Next steps 
- Results

---
## Testing aspects and goals

- @color[black](Isolation & Independence)
- @color[black](Repeatability)
- @color[black](Speed)

Note:
There a couple of aspects, that are crucial for building any test suite

- Tests should not interfere with each other
- You should be able to run any subset of your tests in any order
- You should be able to easily reproduce any test failure
- You should be able to get these results fast

These principles apply to different testing levels.
For unittests when you’re testing small, independent units of your code and as well for integration tests.

---
### Scale

- 400+ developers 
- 250+ active repositories
- Many thousands of tests

Note:
Ideas:
Company is big, many developers, speed of getting a feedback is important, multiply delay by number of devs working on a project

---
### Human factor

Mindset > Testability > Tests

Note:
Ideas
The most important thing is the mindset you have when developing something. 
Then it naturally comes to testable code.
Then tests will come naturally.

---
## Previous state

Note:
I'll provide you with an example of how some parts of our codebase looked like a couple of months before and tell you
some details how it was working and what is wrong with this.

---
### Stack

- Python 2.7 / 3.6 / 3.7
- Flask + connexion
- SQLAlchemy
- PostgreSQL
- Pytest

+++
### Code example
##### Settings

```python
# settings.py
import os

DB_URI = os.environ.get("DB_URI", "postgresql://postgres:postgres@127.0.0.1:5432/postgres")
SSL_CERTIFICATE_PATH = os.environ.get("SSL_CERTIFICATE_PATH")
```

Note:
We have a web application that works with database and we need to test it.
We have a separate module with settings, that are evaluated during the first import.

+++
### Code example

##### Database

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from . import settings


def create_db(uri):
    connect_args = {"application_name": settings.APP_NAME}
    if settings.SSL_CERTIFICATE_PATH:
        connect_args["sslrootcert"] = settings.SSL_CERTIFICATE_PATH
    engine = create_engine(uri)
    session = sessionmaker(bind=engine)
    session = scoped_session(session)
    return engine, session

engine, session = create_db(settings.DB_URI)
```

Note:
We have globally defined engine and session. The session is used in other parts of the code.

+++
### Code example

##### Requests handlers

```python
# handlers.py
from .database import session
from .models import Booking


def create_booking(data):
    booking = Booking(**data)
    session.add(booking)
    session.commit()


def get_booking(id):
    return session.query(Booking).get(id)
```
+++
### Code example

##### Application

```python
# app.py
from connexion.apps.flask_app import FlaskApp
from connexion.resolver import RestyResolver


connexion_app = FlaskApp(__package__)
connexion_app.add_api(
    "path/to/schema.yml",
    validate_responses=True,
    strict_validation=True,
    resolver=RestyResolver("path.to.handlers"),
)
```

Note:
What do you think, is it a real code?

---
## Problems & alternatives

---
### Global settings

```python
# settings.py
import os

DB_URI = os.environ.get("DB_URI", "postgresql://postgres:postgres@127.0.0.1:5432/postgres")
SSL_CERTIFICATE_PATH = os.environ.get("SSL_CERTIFICATE_PATH")
```

Note:
To understand what problems could happen to your test suite and your application when you use global variables we need to look at 
what happens when you use a module with a global variable in its namespace. 
To understand this lets' look how the Python import system works. 

---
### What happens during import

```python
# Check the cache
if name in sys.modules:
    return sys.modules[name]

# Find a module spec
spec = find_spec(name)

# Initialize a module
module = create_module(spec)
init_module_attrs(spec, module)

# Cache the module
sys.modules[spec.name] = module

# Execute the module
code = get_module_code(name)
exec(code, module.__dict__)
# Return from cache
return sys.modules[spec.name]
```

Note:
Python's import machinery will check for already imported module in cache first.
If the module has parent modules, they will be loaded first, then the cache will be checked again.
Then will find a module specification - encapsulation of the module's 
import-related information (absolute name of the module, loader, parent package, etc).
Then module object will be created and initialized with certain attributes from the spec.
Then the module is cached, executed and returned. 
If any errors will occur during the execution, only requested module will be removed from the cache.

+++
### Key points

- Module is an object
- Module's code is executed and attributes are evaluated in a certain context
- Modules are cached
- The cache could be modified even if an error occurs

Note:
If some module is required in two different tests, then it will be executed in a context of the first test and then 
it will be taken from cache in the second test, unless it is not reloaded.
It could lead to various issues if the second test module requires different context to be tested.

+++
### More information

- Source: https://github.com/python/cpython/blob/master/Lib/importlib/_bootstrap.py
- Docs: https://docs.python.org/3/reference/import.html
- PEP: https://www.python.org/dev/peps/pep-0451/

---
### Unit tests examples

```python
import settings
from .database import create_db


def test_create_db_with_cert(monkeypatch):
    monkeypatch.setattr(settings, "SSL_CERTIFICATE_PATH", "/path/to/cert.pem")
    engine, session = create_db("some uri")
    # assert the output
```

---
### Explicit parameters

```python
from .database import create_db

 
def test_create_db_with_cert():
    engine, session = create_db("some uri", ssl_cert_path="/path/to/cert.pem")
    # assert the output
```

---
### Lazy settings. Django example

```
# django/conf/__init__.py

class LazySettings(LazyObject):
    def _setup(self, name=None):
        """Load from env var. Called on first access if not configured already."""
        settings_module = ...
        self._wrapped = Settings(settings_module)
        
    def configure(self, default_settings=global_settings, **options):
        """Manual configuration."""
        if self._wrapped is not empty:
            raise RuntimeError('Settings already configured.')
        holder = UserSettingsHolder(default_settings)
        for name, value in options.items():
            setattr(holder, name, value)
        self._wrapped = holder

settings = LazySettings()
```

Note:
In the case if you need to use some global settings it is much better to keep them lazy like it is done in Django for example.

+++
### Lazy settings. Django example

```
# django/test/utils.py

class override_settings(TestContextDecorator):

    def __init__(self, **kwargs):
        self.options = kwargs

    def enable(self):
        ...

    def disable(self):
        ...
```

Note:
With lazy approach we can override a global settings object without even loading the actual settings.

+++
### Lazy settings. Django example

```python
# database.py
from .conf import settings

...

# test_db.py
from .utils import override_settings


@override_settings(SSL_CERTIFICATE_PATH="/path/to/cert.pem")
def test_create_db_with_cert():
    from .database import create_db
    engine, session = create_db("some uri", ssl_cert_path="/path/to/cert.pem")
    # assert the output

```
---
### Global DB session

```python
# database.py
engine, session = create_db(settings.DB_URI)
```

Note:
Unfortunately the settings are accessed on the module level and we need to override it before the module is loaded.
We could apply a similar approach to the DB session, but before that let's look how does it work.

+++
### How session works

##### It is lazy

```python
class scoped_session(object):
    session_factory = None

    def __init__(self, session_factory, scopefunc=None):
        self.session_factory = session_factory

        if scopefunc:
            self.registry = ScopedRegistry(session_factory, scopefunc)
        else:
            self.registry = ThreadLocalRegistry(session_factory)
            
def instrument(name):
    def do(self, *args, **kwargs):
        return getattr(self.registry(), name)(*args, **kwargs)
    return do


for meth in Session.public_methods:
    setattr(scoped_session, meth, instrument(meth))
```

Note:
Scoped session is lazy. It takes a factory and it doesn't call it immediately, but proxies all calls to the registry, which
initializes the factory lazily as well. 

+++
### How session works

##### It is thread-local

```python
class ThreadLocalRegistry(ScopedRegistry):

    def __init__(self, createfunc):
        self.createfunc = createfunc
        self.registry = threading.local()

    def __call__(self):
        try:
            return self.registry.value
        except AttributeError:
            val = self.registry.value = self.createfunc()
            return val
```

Note:
The registry is thread-local - values will be different for separate threads.

+++
### How session works

#### It uses an identity map

```python
import weakref

class IdentityMap(object):
    def __init__(self):
        self._dict = {}
        self._modified = set()
        self._wr = weakref.ref(self)
    ...

class Session:

    def __init__(self, *args, **kwargs):
        self.identity_map = IdentityMap()
        ...
```

Note:
An identity map is basically a cache between your application code and the database. 
If the requested data has already been loaded from the database, the identity map returns the same instance 
of the already instantiated object, but if it has not been loaded yet, it loads it and stores the new object in the map.

---
### Handlers tests

```python
from .handlers import create_booking, get_booking


def test_create_booking():
    email = "test@test.com"
    booking = create_booking(email=email)
    assert booking.email == email


def test_get_booking():
    assert get_booking(1) is None
```

---
### State after the first test

- Identity map is modified
- Changes are committed to the DB

Note:
The new booking, created during the first test is saved in the identity map and as well it is committed to the DB.
This breaks isolation of our test cases.
Sometimes some of these issues could be acceptable or they could be managed with some framework (like Django test suite)
But if you want to implement global entities by yourself you should at least be aware of the following aspects.

---
### Globals check list

- Module caching
- Different contexts
- Laziness
- Thread-safety
- Weak references

Note:
All your modules are executed and cached. The context of execution could be not exactly what you need.
Laziness plays well, it postpones evaluation until the very last moment and at least you have more control over it.
Your global variable could be accessed by different threads - use locks and thread-local storage for that
If you want to cache something - consider having weak references. 
Objects will not be kept only because it is cached somewhere.

---
### How to handle all of this?

Note:
Let's go from ad-hoc solutions to something better.

---
### Monkey-patching

```python
# conftest.py
import database


@pytest.fixture(scope='session', autouse=True)
def db_schema(db_uri):
    engine = create_engine(db_uri)

    # Create extensions, tables, etc

    Session = orm.scoped_session(orm.sessionmaker())
    Session.configure(bind=engine)
    session = Session()

    yield session

    Session.remove()
    # Drop tables, extensions, etc


@pytest.fixture(autouse=True)
def db(db_schema, monkeypatch):
    db_schema.begin_nested()
    monkeypatch.setattr(database, 'db', db_schema)

    yield db_schema

    db_schema.rollback()
    db_schema.close()
```

Note:
Here is an example of how global objects could be handled in tests. Monkey-patching.

---
### What is wrong?

@ul
- @color[black](Complexity grows very fast)
- @color[black](Weaker tests)
- @color[black](Decreases code coverage)
- @color[black](Fragile test suite)
- @color[black](Could affect test suite running time)
@ulend

Note:
Whats wrong with that? Complexity grows dramatically fast
Your tests will be weaker, because they test less real code and more mocked code.
It decreases the actual code coverage. 
Also, the test suite becomes more fragile, since some tests could depend on the execution order. 
If you need to create and destroy many objects for your test it could affect speed of your test suite execution.
To run tests on every commit you need fast tests. When it is too long you're switching to another context, e.g. to browser.
After some time your tests will finish, but Facebook on your tab will not.

---
### It could fix some symptoms, but it doesn't fix the problem

<img src="articles/testable-code-making-the-testing-world-better/v1/presentation/assets/img/fix-problem.jpg" alt="Fix problem" width="600px"/>

Note:
In large projects, it could lead to monkey patching a significant amount of different modules.

---
### There is a better way

Note:
The global state in the previous examples is hardly predictable. Let’s change it and make it manageable.
The first step is to take control when the object is initialised. 
We want to initialise it only when we need it; just in the desired context.

---
@transition[none]
@snap[north]
<h3>Deferred initialization</h3>
@snapend

Note:
Flask has a beautiful way of solving this problem — init_app pattern. 
It allows you to isolate some global state in an object and control when to initialise it. 
Also, it used to register some teardown logic for this global object.

+++
@transition[none]
@snap[north]
<h3>Deferred initialization</h3>
@snapend

```python
# database.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# conftest.py
from flask import Flask
import database


@pytest.fixture(scope="session")
def db():
    app = Flask(__name__)
    database.db.init_app(app)
    database.db.create_all()    
    yield database.db
    database.db.drop_all()


@pytest.fixture(autouse=True)
def session(db):
    db.session.begin_nested()
    yield db.session
    db.session.rollback()
    db.session.remove()
```

@[1-5](Database)
@[6-31])(New shiny fixtures)

##### `Flask-SQLAlchemy` 

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
## Next steps

---
### Pytest for factories

```python
class User(Base):
    id = Column(Integer(), primary_key=True)
    name = Column(String(20))
```

+++
### Pytest for factories

```python
@pytest.fixture
def user_factory():

    defaults = {
        "name": "John Doe"
    }

    def _factory(**kwargs):
        return User(**{**defaults, **kwargs})

    return _factory

```

+++
### Pytest for factories

```python
def test_factory_fixture(user_factory):
    assert user_factory().name == 'John Doe'
```
---
@transition[none]
@snap[north]
<h3>Factory boy</h3>
@snapend

##### `factoryboy`

```python
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
@transition[none]
@snap[north]
<h3>Dependency injection</h3>
@snapend

```python
def create_booking(session, data):
    booking = Booking(**data)
    session.add(booking)
    session.commit()
```

Note:
There is another technique that was used in the previous examples but wasn’t mentioned explicitly. Dependency injection.

+++
@transition[none]
@snap[north]
<h3>Dependency injection</h3>
@snapend

### Redis-py connection pool + tests

```python
class StrictRedis(object):

    def __init__(self, connection_pool=None, **kwargs):
        if not connection_pool:
            ...
            connection_pool = ConnectionPool(**kwargs)
        self.connection_pool = connection_pool
```

+++
@transition[none]
@snap[north]
<h3>Dependency injection</h3>
@snapend

### Redis-py connection pool

#### Tests
```python
class DummyConnection(object):
    description_format = "DummyConnection<>"

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.pid = os.getpid()


class TestConnectionPool(object):
    def get_pool(self, connection_kwargs=None, max_connections=None,
                 connection_class=DummyConnection):
        connection_kwargs = connection_kwargs or {}
        return redis.ConnectionPool(
            connection_class=connection_class,
            max_connections=max_connections,
            **connection_kwargs)

    def test_connection_creation(self):
        connection_kwargs = {'foo': 'bar', 'biz': 'baz'}
        pool = self.get_pool(connection_kwargs=connection_kwargs)
        connection = pool.get_connection('_')
        assert isinstance(connection, DummyConnection)
        assert connection.kwargs == connection_kwargs
```

---
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
### Multiple inheritance

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .models import Booking


class SessionFactory:

    def __init__(self, db_uri):
        self.db_uri = db_uri

    def create_engine_and_session(self):
        engine = create_engine(self.db_uri)
        session = sessionmaker(bind=engine)
        session = scoped_session(session)
        return engine, session


class BookingFactory(SessionFactory):

    def create_booking(self, data):
        session = self.create_engine_and_session()
        booking = Booking(**data)
        session.add(booking)
        session.commit()
```

+++
### Multiple inheritance

```python

class MockSessionFactory(SessionFactory):

    def create_engine_and_session(self):
        engine = Mock()
        session = Mock()
        # Setup mocks
        return engine, session


class MockedBookingFactory(BookingFactory, MockSessionFactory):
    pass
```

+++
### Multiple inheritance

Consider as an alternative

Raymond Hettinger: https://www.youtube.com/watch?v=EiOglTERPEo

---
## Database

### New database for each testcase with `testing.postgresql`

```python
import pytest
import testing.postgresql


@pytest.fixture
def db_uri():
    with testing.postgresql.Postgresql() as db:
        yield db.url()


@pytest.fixture
def db(db_uri):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    database.db.init_app(app)
    database.db.create_all()    
    yield database.db
    database.db.drop_all()
```

---
## Database

### Truncate all data for each testcase

```python
import pytest
import testing.postgresql


@pytest.fixture(scope="session")
def db_uri():
    with testing.postgresql.Postgresql() as db:
        yield db.url()


@pytest.fixture(scope="session")
def db(db_uri):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    database.db.init_app(app)
    database.db.create_all()    
    yield database.db
    database.db.drop_all()


@pytest.fixture(autouse=True)
def session(db):
    yield db.session
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
```

---
### Database

### Wrap each testcase into transaction
### + pytest example

```python
@pytest.fixture(autouse=True)
def session(db):
    db.session.begin_nested()
    yield db.session
    db.session.rollback()
    db.session.remove()
```

---
### Database

### Consider using `pytest-pgsql`

https://github.com/CloverHealth/pytest-pgsql

---
### Speed up the test suite

- Put DB in RAM
- Disable DB logs
- Split your test suite
- Run in parallel

---
## Results

- Simpler codebase
- Less unused code
- Faster tests
- Faster code review

---
## Thank you

- https://github.com/Stranger6667
- https://twitter.com/Stranger6667