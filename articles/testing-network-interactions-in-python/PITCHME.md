### @color[black](Testing)
### @color[black](network interactions)
### @color[black](in Python)

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
- Pytest + Factory Boy

+++
### Example
#### Models

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Transaction(db.Model):
    """Payment transaction."""

    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(db.Integer, nullable=False)

    amount = db.Column(db.Numeric, nullable=False)
    currency = db.Column(db.String(3), nullable=False)

    amount_eur = db.Column(db.Numeric, nullable=False)


class ExchangeRate(db.Model):
    """Current ratios to EUR."""

    currency = db.Column(db.String(3), primary_key=True)
    ratio = db.Column(db.Numeric, nullable=False)
```

+++
### Example
#### Application

```python
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://127.0.0.1:5432/test"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    from .models import db

    db.init_app(app)

    return app
```

@[4-6]
@[8-10]

+++
### Example
#### Payments

```python
from decimal import Decimal

from . import exchange
from .models import db, Transaction

def save_transaction(booking_id: int, amount: Decimal, currency: str):
    """We need to store EUR amount as well."""
    amount_eur = exchange.to_eur(amount, currency)

    transaction = Transaction(booking_id=booking_id, amount=amount, currency=currency, amount_eur=amount_eur)
    db.session.add(transaction)
    db.session.commit()
    return transaction
```

@[7]
@[9-11]

+++
### Example
#### Exchange

```python
from decimal import Decimal

from .exceptions import NoExchangeRateError
from .models import ExchangeRate

def to_eur(amount: Decimal, currency: str):
    """Convert to EUR."""
    if currency == "EUR":
        return amount
    rate = ExchangeRate.query.filter_by(currency=currency).one_or_none()
    if not rate:
        raise NoExchangeRateError("No such rate")
    return rate.ratio * amount
```

@[6-13]

+++
### Example

##### factories.py

```python
from factory import Faker
from factory.alchemy import SQLAlchemyModelFactory

from booking import models

session = models.db.create_scoped_session()


class ExchangeRateFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.ExchangeRate
        sqlalchemy_session = session
        sqlalchemy_session_persistence = "commit"

    currency = Faker("pystr", min_chars=3, max_chars=3)
    ratio = Faker("pydecimal", positive=True)
```

+++
### Example
##### conftest.py

```python
import pytest
from pytest_factoryboy import register

from booking.app import create_app
from booking.models import db

from . import factories

register(factories.ExchangeRateFactory)


@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        yield app


@pytest.fixture
def database(app):
    db.create_all()
    yield
    db.session.commit()
    db.drop_all()
```

+++
### Example
##### test_payments.py

```python
from decimal import Decimal

import pytest

from booking.exceptions import NoExchangeRateError
from booking.payments import save_transaction

pytestmark = [pytest.mark.usefixtures("database")]

def test_save_transaction(exchange_rate_factory):
    exchange_rate_factory(currency="CZK", ratio="25.5")
    transaction = save_transaction(1, Decimal(10), "CZK")
    assert transaction.amount_eur == Decimal(255)

def test_save_transaction_no_rates():
    with pytest.raises(NoExchangeRateError, message="No such rate"):
        save_transaction(1, Decimal(10), "CZK")
```

---
## Cutting out

---
### New exchange code (sync)

```python
from decimal import Decimal

import requests

from .exceptions import NoExchangeRateError

def to_eur(amount: Decimal, currency: str):
    response = requests.get("https://rates.kiwi.com/to_eur", params={"amount": amount, "currency": currency})
    data = response.json()
    try:
        response.raise_for_status()
    except requests.HTTPError:
        if data["detail"] == "No such rate":
            raise NoExchangeRateError
        raise
    return Decimal(data["result"])
```

+++
### Ad hoc tests

```python
from decimal import Decimal

import pytest

from booking.exceptions import NoExchangeRateError
from booking.sync.payments import save_transaction

pytestmark = [pytest.mark.usefixtures("database")]

def test_save_transaction(mocker):
    mocker.patch("booking.sync.exchange.to_eur", return_value=Decimal(255))
    transaction = save_transaction(1, Decimal(10), "CZK")
    assert transaction.amount_eur == 255

def test_save_transaction_no_rates(mocker):
    mocker.patch("booking.sync.exchange.to_eur", side_effect=NoExchangeRateError("No such rate"))
    with pytest.raises(NoExchangeRateError, message="No such rate"):
        save_transaction(1, Decimal(10), "CZK")
```

+++
### More configurable approach

```python
@pytest.fixture
def setup_rates(mocker):

    def inner(value):
        if isinstance(value, Exception):
            kwargs = {"side_effect": value}
        else:
            kwargs = {"return_value": value}
        mocker.patch("booking.sync.exchange.to_eur", **kwargs)

    return inner


def test_save_transaction(setup_rates):
    setup_rates(Decimal(255))
    transaction = save_transaction(1, Decimal(10), "CZK")
    assert transaction.amount_eur == 255


def test_save_transaction_no_rates(setup_rates):
    setup_rates(NoExchangeRateError("No such rate"))
    with pytest.raises(NoExchangeRateError, message="No such rate"):
        save_transaction(1, Decimal(10), "CZK")
```

+++
### Alternative

```python
@pytest.fixture(autouse=True)
def setup(request, mocker):
    mark = request.node.get_closest_marker("setup_rates")
    if mark:
        mocker.patch("booking.sync.exchange.to_eur", **mark.kwargs)

@pytest.mark.setup_rates(return_value=Decimal(255))
def test_save_transaction():
    transaction = save_transaction(1, Decimal(10), "CZK")
    assert transaction.amount_eur == 255
```
---
### Async version with aiohttp

```python
from decimal import Decimal

import aiohttp

from .exceptions import NoExchangeRateError

async def to_eur(amount: Decimal, currency: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://rates.kiwi.com/to_eur", params={"amount": amount, "currency": currency}
        ) as response:
            data = await response.json()
            try:
                response.raise_for_status()
                return Decimal(data["result"])
            except aiohttp.ClientResponseError:
                if data["detail"] == "No such rate":
                    raise NoExchangeRateError
                raise
```
+++
### Async payments

```python
from . import exchange

async def save_transaction(booking_id: int, amount: Decimal, currency: str):
    """We need to store EUR amount as well."""
    amount_eur = await exchange.to_eur(amount, currency)

    return await asyncpg_save(booking_id, amount, currency, amount_eur)
```
+++
### Ad hoc tests

```python
pytestmark = [pytest.mark.usefixtures("database"), pytest.mark.asyncio]


async def test_save_transaction(mocker):

    async def coro():
        return Decimal(255)

    mocker.patch("booking.aio.exchange.to_eur", return_value=coro())
    transaction = await save_transaction(1, Decimal(10), "CZK")
    assert transaction.amount_eur == 255


async def test_save_transaction_no_rates(mocker):
    mocker.patch("booking.aio.exchange.to_eur", side_effect=NoExchangeRateError("No such rate"))
    with pytest.raises(NoExchangeRateError, message="No such rate"):
        await save_transaction(1, Decimal(10), "CZK")
```

---
### Pros & cons

##### Pros:
- Easy to setup

##### Cons:
- Becomes messy very fast
- Doesn't actually test API wrapper

Note:
These kind of tests are good if you can afford saying - I don't care what this part does internally, 
I just assume that it should return this data in this situation.
It could work for small and simple parts from time to time or it could work as a temporary solution.
I personally can afford myself this level of confidence in the code

---
### Generic libs

#### Responses

```python

def test_save_transaction(responses):
    responses.add(responses.GET, "https://rates.kiwi.com/to_eur", body='{"result": 255}')
    transaction = save_transaction(1, Decimal(10), "CZK")
    assert transaction.amount_eur == 255
```
+++
### Emulate exception


```python
def test_save_transaction_no_rates(responses):
    responses.add(responses.GET, "https://rates.kiwi.com/to_eur", body=NoExchangeRateError("No such rate"))
    with pytest.raises(NoExchangeRateError, message="No such rate"):
        save_transaction(1, Decimal(10), "CZK")
```

+++
### Dynamic response

```python

@pytest.fixture
def setup_rates(responses):
    def request_callback(request):
        parsed = urlparse(request.url)
        query_string = dict(parse_qsl(parsed.query))
        amount = Decimal(query_string["amount"])
        currency = query_string["currency"]
        rates = {
            "CZK": Decimal("25.5")
        }
        try:
            rate = rates[currency]
            value = json.dumps({"result": str(rate * amount)})
        except KeyError:
            value = NoExchangeRateError("No such rate")
        return 200, {}, value

    responses.add_callback(responses.GET, "https://rates.kiwi.com/to_eur", callback=request_callback)


@pytest.mark.usefixtures("setup_rates")
def test_save_transaction_dynamic(responses):
    ...

```
+++
### Pros & cons

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

Pros:
- Convenient API
- Multiple requests

Cons:
- A lot of manual work

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