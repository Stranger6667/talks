#### Testing network interactions in Python

---
### Who am I

- @color[black](Tech Lead at kiwi.com)
- @color[black](Prague, Czech Republic)
- @color[black](Love Python & open-source)

---
### Case study

#### Monolithic app

##### Flights booking

+++
### Case study

#### Microservices 

+++
### Case study

#### Looking for a good candidate

+++
### Case study

#### Exchange rates

Note:
Code example

+++
### Case study

#### Interact over network

---
### Overview

**Project intro**

- Code
- Integration tests 

**Mocked network**

- Ad hoc
- Generic
- Cassettes

**Next steps**

- Real network

Note:
- monolith
- in progress (no real need for an external service)
- Real microservice

---
### Stack

- Python 3.7
- Flask + connexion
- SQLAlchemy
- PostgreSQL
- Pytest

+++
### Booking code

+++
### Exchange code

+++
### Tests

---
## Cutting out

---
### New exchange code (sync)

Note:
API wrapper

---
### Async version with aiohttp

---
### Ad hoc tests

+++
### Async version

+++
### More configurable approach

+++
### Async version

+++
### Pros & cons

---
### Generic libs

#### Responses

+++
### Emulate exception

+++
### Pros & cons

- Requests - only

---
### Async way

#### Aio-responses

+++
### Pros & cons

---
### Sync and async

#### Pook

+++
### Examples

+++
### Pros & cons

---
### Generic libs summary

---
### Cassettes

Notes:
Description

+++
### Libraries

VCRPy, Betamax (requests-only)

+++
### Example

+++
### Cassette

+++
### Record modes

+++
### HTTP libraries support

+++
### Pros & cons

---
## Real network

+++
### Docker

Note:
Architectural overview

+++
### Libraries examples

+++
### Pros & cons

---
### Summary

---
### Thank you