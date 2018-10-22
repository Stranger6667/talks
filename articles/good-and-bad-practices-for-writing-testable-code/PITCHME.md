---?image=articles/good-and-bad-practices-for-writing-testable-code/assets/img/background.png


@snap[north-west]
<br>
<b style="font-size:52px; font-family: 'Trebuchet MS'">Хорошие и плохие практики для<br>написания тестируемого кода</b>
<br><br>
<p style="font-size:52px; font-family: 'Trebuchet MS'">Дмитрий Дыгало (kiwi.com)</p>
@snapend

---
### Who am I

- @color[black](Тимлид в KIWI.COM)
- @color[black](Прага, Чехия)
- @color[black](Python & open-source)

@snap[south]
<b>1</b>
@snapend

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

- Важные аспекты и цели тестирования
- Что было раньше
- Проблемы и варианты их решения
- Следующие шаги
- Результаты

---
### Aspects and goals

- @color[black](Изоляция и независимость)
- @color[black](Воспроизводимость)
- @color[black](Скорость)

---
### Stack

- Python 2.7 / 3.6 / 3.7
- Flask + connexion
- SQLAlchemy
- PostgreSQL
- Pytest

---
### Example
##### Project structure

<img src="articles/good-and-bad-practices-for-writing-testable-code/assets/img/overview.png" width="600px"/>

+++
### Example
##### Settings

```python
# settings.py
import os

DB_URI = os.environ.get(
    "DB_URI", 
    "postgresql://127.0.0.1/postgres"
)
APP_NAME = "projectA"
SSL_CERTIFICATE_PATH = os.environ.get("SSL_CERTIFICATE_PATH")
```

Note:
We have a web application that works with database and we need to test it.
We have a separate module with settings, that are evaluated during the first import.

+++
### Example

##### Database

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from . import settings

def create_db(uri):
    args = {"application_name": settings.APP_NAME}
    if settings.SSL_CERTIFICATE_PATH:
        args["sslrootcert"] = settings.SSL_CERTIFICATE_PATH
    engine = create_engine(
        uri,
        connect_args=args
    )
    session = sessionmaker(bind=engine)
    session = scoped_session(session)
    return engine, session

engine, session = create_db(settings.DB_URI)
```

@[7-9]
@[10-16]
@[18]

Note:
We have globally defined engine and session. The session is used in other parts of the code.

+++
### Example

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

@[5-8]
@[10-11]

+++
### Example

##### Application

```python
# app.py
from connexion.apps.flask_app import FlaskApp
from connexion.resolver import RestyResolver


connexion_app = FlaskApp(__package__)
connexion_app.add_api(
    "path/to/schema.yml",
    resolver=RestyResolver("path.to.handlers"),
)
```

Note:
What do you think, is it a real code?

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

@[3-6]
@[8-9]

---
## Problems & alternatives

---
### Global settings

```python
# settings.py
import os

DB_URI = os.environ.get(
    "DB_URI", 
    "postgresql://127.0.0.1/postgres"
)

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

@[1-3]
@[5-6]
@[8-10]
@[12-13]
@[15-17]
@[19-20]

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

- Модуль это объект
- Код модуля выполняется в определенном контексте
- Модули кэшируются
- Кэш может быть модифицирован даже при ошибки во время импорта

Note:
If some module is required in two different tests, then it will be executed in a context of the first test and then 
it will be taken from cache in the second test, unless it is not reloaded.
It could lead to various issues if the second test module requires different context to be tested.

---
### Global DB session

```python
# database.py
engine, session = create_db(settings.DB_URI)
```

+++
### How session works

##### It is lazy

```python
class scoped_session:

    def __init__(self, session_factory, scopefunc=None):
        ...
        if scopefunc:
            self.registry = ScopedRegistry(
                session_factory, 
                scopefunc
            )
        else:
            self.registry = ThreadLocalRegistry(
                session_factory
            )
            
def instrument(name):
    def do(self, *args, **kwargs):
        method = getattr(self.registry(), name)
        return method(*args, **kwargs)
    return do

for meth in Session.public_methods:
    setattr(scoped_session, meth, instrument(meth))
```

@[11-13]
@[15-20]
@[21-22]

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

@[5]
@[8-12]

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

@[1-7]
@[10-13]

Note:
An identity map is basically a cache between your application code and the database. 
If the requested data has already been loaded from the database, the identity map returns the same instance 
of the already instantiated object, but if it has not been loaded yet, it loads it and stores the new object in the map.

---
### State after the first test

- `settings` / `database` закэшированы в `sys.modules`  
- Identity map содержит в себе экземпляр модели
- Изменения внесены в базу

Note:
The new booking, created during the first test is saved in the identity map and as well it is committed to the DB.
This breaks isolation of our test cases.
Sometimes some of these issues could be acceptable or they could be managed with some framework (like Django test suite)
But if you want to implement global entities by yourself you should at least be aware of the following aspects.

---
### Globals check list

- Кэширование модулей
- Различные контексты выполнения
- Ленивость
- Потокобезопасность
- Слабые ссылки

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

@pytest.fixture(scope="session", autouse=True)
def db():
    engine = create_engine(
        "postgresql://127.0.0.1/another_db"
    )

    # Create extensions, tables, etc

    Session = orm.scoped_session(orm.sessionmaker())
    Session.configure(bind=engine)
    session = Session()

    yield session

    Session.remove()
    # Drop tables, extensions, etc


@pytest.fixture
def session(db, monkeypatch):
    db.begin_nested()
    monkeypatch.setattr(database, "db", db)

    yield db

    db.rollback()
    db.close()
```

@[4-5]
@[6-8]
@[12-16]
@[18]
@[22-25]
@[27]
@[29-30]

Note:
Here is an example of how global objects could be handled in tests. Monkey-patching.

---
### What is wrong?

@ul
- @color[black](Сложность растет очень быстро)
- @color[black](Тесты становятся слабее)
- @color[black](Уменьшает тестовое покрытие)
- @color[black](Тесты легче сломать)
- @color[black](Скорость выполнения тестов может пострадать)
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

### There is a better way

Note:
In large projects, it could lead to monkey patching a significant amount of different modules.
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
<h4>Deferred initialization</h3>
@snapend

```python
# database.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# conftest.py
import pytest
from flask import Flask
import database

@pytest.fixture
def app():
    return Flask("test")

@pytest.fixture(scope="session")
def db(app):
    database.db.init_app(app)
    database.db.create_all()    
    yield database.db
    database.db.drop_all()

@pytest.fixture
def session(db):
    db.session.begin_nested()
    yield db.session
    db.session.rollback()
    db.session.remove()
```

@[2-4]
@[11-13]
@[15-20]
@[22-27]

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
- @color[black](Управляемая инициализация базы)
- @color[black](Нет monkey-patching'а)
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

...
```

@[3-5]
@[7-10]
@[12]
@[17-19]

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
- @color[black](Изоляция. Приложение создается после запуска тестовой сессии)
- @color[black](Гибкость. Широкие возможности параметризации)
@ulend

Note:
- Isolate the side-effects of creating an application on the module-level. 
- Flexibility — multiple apps and/ore different settings. It’s available as a fixture, which provides more flexibility (e.g., parametrization)

---
## Next steps

---
### Database

#### New database for each testcase with `testing.postgresql`

```python
# conftest.py
import pytest
import testing.postgresql

@pytest.fixture
def db_uri():
    with testing.postgresql.Postgresql() as db:
        yield db.url()

@pytest.fixture
def app(db_uri):
    return create_app(
        "app.settings.TestSettings", 
        SQLALCHEMY_DATABASE_URI=db_uri
    )

@pytest.fixture
def db(app):
    database.db.init_app(app)
    database.db.create_all()    
    yield database.db
    database.db.drop_all()
```

@[5-8]
@[10-15]
@[17-22]

---
### Database

#### Truncate all data for each testcase

```python
# conftest.py
...

@pytest.fixture(scope="session")
def db_uri():
    ...

...

@pytest.fixture
def session(db):
    yield db.session
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
```

@[4-5]
@[10-15]

---
### Database

#### Wrap each testcase into transaction

```python
# conftest.py
...

@pytest.fixture
def session(db):
    db.session.begin_nested()
    yield db.session
    db.session.rollback()
    db.session.remove()
```

---
### Database

#### Consider using `pytest-pgsql`

https://github.com/CloverHealth/pytest-pgsql

---
### Speed up the test suite

- База в памяти
- Отключение логов
- Шаблоны базы / переиспользование существующей
- Разделение и параллельное выполнение

---
## Results

- Более простой код
- Меньше неиспользованного кода
- Выше скорость выполнения тестов

---
## Thank you

- https://github.com/Stranger6667
- https://twitter.com/Stranger6667
