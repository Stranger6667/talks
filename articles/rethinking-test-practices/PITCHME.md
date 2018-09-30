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

---
### Key points

---
### Unit tests examples

---
### Lazy settings. Django example

---
### Explicit parameters

---
### Global DB session

---
### It is lazy

---
### It is thread-local

---
### Identity map

---
### State after the first test

---
### How to handle all of this?

---
### Monkey-patching

---
### What is wrong?

---
### Symptoms

---
### Make it better

---
### Deferred init

---
### Flask-SQLAlchemy

---
### Benefits

---
### Globals check list

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
 