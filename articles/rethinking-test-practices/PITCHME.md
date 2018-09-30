### @color[orange](Rethinking your testing practices)

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

Structure. We will talk about:
- Goals
- Previous / Current state 
- Particular tech problems + alternatives
- General problems + improvements 
- Results

---
### Testing aspects. 

---
### Applying these aspects at scale

Our scale and importance of testing

---
### Human factor

----------------------
---
### Code example

---
### Tests example

---
### Running example

---
### What is wrong

---
### Global settings

---
### What happens during import

```python
# Check the cache
if name in sys.modules:
    return sys.modules[name]

# Load parent modules if exist
if has_parents(name):
    load_parents()
    # Check the cache again
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

#### Ugly examples of unit tests for functions, that use global settings

---
### Lazy settings. Django example

---
### Explicit parameters

---
### Global DB session

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
To understand what is going on during these tests, lets look at how the SQLAlchemy session works.
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
### State after the first test

- Identity map is modified
- Changes are committed to the DB

Note:
The new booking, created during the first test is saved in the identity map and as well it is committed to the DB.
This breaks isolation of our test cases.
Sometimes some of these issues could be acceptable or they could be managed with some framework (like Django test suite)
But if you want to implement global entities by yourself you should at least be aware of the following aspects.

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
### Make it better

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

##### `Flask-SQLAlchemy` 

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

----------------------------------
---
### App factory

---
### Pytest for factories

---
### Factory boy

---
### Dependency injection

---
### Examples flask-sqlalchemy / redis-py

---
### Benefits

---
### Multiple inheritance 

---
### DB 1, 2, 3

---
### Speed up the test suite
Optimize db, put in memory
Split, parallelize

---
### What happened to our test suite speed

---
### Coverage

Remove unused branches

---
### MR review time.

---
### How to treat tests & testability
 