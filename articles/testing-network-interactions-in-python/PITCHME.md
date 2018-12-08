### @color[black](Testing network interactions)
### @color[black](in Python)
#### @color[black](part 1)

---
### Who am I

- @color[black](Tech Lead at kiwi.com)
- @color[black](Live in Prague, Czech Republic)
- @color[black](Graduated as an information security specialist)
- @color[black](Python since 2010)
- @color[black](Maintain django-money (Money fields for Django))

---
@transition[none]
@snap[north]
### Overview
@snapend

@snap[west span-30]
<div id="boxed-text-box" class="bg-green text-white">
    <div id="boxed-text-title-box">
        <span id="boxed-text-title" style="font-size: 80%">Project intro</span>
    </div>
    <snap style="font-size: 70%">Code</snap><br>
    <snap style="font-size: 70%">Tests</snap>
</div>
@snapend

@snap[midpoint span-30]
<div id="boxed-text-box" class="bg-green text-white">
    <div id="boxed-text-title-box">
        <span id="boxed-text-title" style="font-size: 80%">Mocked network</span>
    </div>
    <snap style="font-size: 70%">Ad hoc</snap><br>
    <snap style="font-size: 70%">Generic tools</snap><br>
    <snap style="font-size: 70%">Cassettes</snap>
</div>
@snapend

@snap[east span-30]
<div id="boxed-text-box" class="bg-green text-white">
    <div id="boxed-text-title-box">
        <span id="boxed-text-title" style="font-size: 80%">Real examples</span>
    </div>
    <snap style="font-size: 70%">API integration</snap><br>
    <snap style="font-size: 70%">Refactoring</snap>
</div>
@snapend

Note:
- monolith
- in progress (no real need for an external service)

---
### Case study

<img src="articles/testing-network-interactions-in-python/img/monolith.jpg" alt="Monolith" height="400px"/>

##### Monolithic app for flights booking

Note:
Let's imagine that we built an application for flights booking a couple of years ago.
And after some time it became big, ugly and unmaintainable.

+++
### Case study 

<img src="articles/testing-network-interactions-in-python/img/microservices.png" alt="Microservices" height="400px"/>

##### Microservices

Note:
No talk about microservices can go without a container ship image. Right?
A usual way to go nowadays.

+++
### Case study

<img src="articles/testing-network-interactions-in-python/img/structure.png" alt="Structure" height="400px"/>

##### Looking for a good candidate

Note:
So, we start searching for a good piece of code that we can cut out as a microservice.
And we found one - exchange rates. They are quite independent 

+++
### Case study

<img src="articles/testing-network-interactions-in-python/img/new_structure.png" alt="New structure" height="400px"/>

##### Interact over network

Note:
Our new approach could look like this. The booking app will interact with the exchange rates app over the network. 
It is amazing, isn't it?
Let's inspect the code we have so far.

---
### Stack

- Python 3.7
- Flask + connexion
- SQLAlchemy
- PostgreSQL
- Pytest

+++
@snap[north]
### Code
@snapend

```python
...
class Transaction(db.Model):
    """Payment transaction."""
    ...
    amount = db.Column(db.Numeric, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    amount_eur = db.Column(db.Numeric, nullable=False)

class ExchangeRate(db.Model):
    """Current ratios to EUR."""
    currency = db.Column(db.String(3), primary_key=True)
    ratio = db.Column(db.Numeric, nullable=False)
```

@[2-7]
@[9-12]

#### Models

Note:
We have two models, transactions and exchange rates to EUR.

+++
@snap[north]
### Code
@snapend

```python
...

def save_transaction(booking_id, amount, currency):
    """We need to store EUR amount as well."""
    amount_eur = exchange.to_eur(amount, currency)

    transaction = Transaction(
        booking_id=booking_id, 
        amount=amount, 
        currency=currency, 
        amount_eur=amount_eur
    )
    db.session.add(transaction)
    db.session.commit()
```

@[3-5]
@[7-14]

#### Payments

Note:
The only place we use the exchange rate is the payment module.
We need to store payment transaction amount in EUR as well as in the original currency.

+++
@snap[north]
### Code
@snapend

```python
...
def to_eur(amount, currency):
    """Convert to EUR."""
    rate = ExchangeRate.query.filter_by(
        currency=currency
    ).one_or_none()
    if not rate:
        raise NoExchangeRateError("No such rate")
    return amount / rate.ratio
```

#### Exchange

+++
@snap[north]
### Tests
@snapend

```python
...

pytestmark = [pytest.mark.usefixtures("database")]

def test_save_transaction(exchange_rate_factory):
    exchange_rate_factory(currency="CZK", ratio="25.5")
    transaction = save_transaction(1, Decimal(2550), "CZK")
    assert transaction.amount_eur == Decimal(100)

def test_save_transaction_no_rates():
    with pytest.raises(
        NoExchangeRateError, 
        message="No such rate"
    ):
        save_transaction(1, Decimal(10), "NOK")
```

@[5-8]
@[10-15]

##### test_payments.py

---
@snap[north]
### Cutting out
@snapend

<img src="articles/testing-network-interactions-in-python/img/cake-cut.jpg" alt="Cutting out" height="400px"/>

Note:
Ok, lets cut this lovely application.

---
@snap[north]
### New exchange code (sync)
@snapend

```python
...

def to_eur(amount, currency):
    response = requests.get(
        "http://127.0.0.1:5000/to_eur", 
        params={"amount": amount, "currency": currency}
    )
    data = response.json()
    try:
        response.raise_for_status()
    except requests.HTTPError:
        if data["detail"] == "No such rate":
            raise NoExchangeRateError
        raise
    return Decimal(data["result"])
```

@[4-8] Request to 127.0.0.1
@[9-14] Some error handling
@[15]

Note:
Our exchange rates service will work on localhost for a while.
And use requests to get the data.

+++
@snap[north]
### Ad hoc tests
@snapend

<img src="articles/testing-network-interactions-in-python/img/pretend-doesnt-exist.jpeg" alt="Pretend" height="400px"/>

##### Let's pretend that the new code doesn't exist

+++
@snap[north]
### Ad hoc tests
@snapend

```python
...

def test_save_transaction(mocker):
    mocker.patch(
        "booking.sync.exchange.to_eur", 
        return_value=Decimal(100)
    )
    ...

def test_save_transaction_no_rates(mocker):
    mocker.patch(
        "booking.sync.exchange.to_eur", 
        side_effect=NoExchangeRateError("No such rate")
    )
    ...
```

@[4-7]
@[11-14]

##### pytest-mock

+++
@snap[north]
### More configurable approach
@snapend

```python
@pytest.fixture
def setup_rates(mocker):

    def inner(**kwargs):
        ...  # Your awesome dynamic configuration
        mocker.patch("booking.sync.exchange.to_eur", **kwargs)

    return inner

def test_save_transaction(setup_rates):
    setup_rates(return_value=Decimal(100))
    ...

def test_save_transaction_no_rates(setup_rates):
    setup_rates(
        side_effect=NoExchangeRateError("No such rate")
    )
    ...
```

@[1-8]
@[10-11]
@[14-17]

+++
@snap[north]
### Alternative
@snapend

```python
def setup_rates(mocker, **kwargs):
    ...  # Your awesome dynamic configuration
    mocker.patch("booking.sync.exchange.to_eur", **kwargs)

@pytest.fixture(autouse=True)
def setup(request):
    mark = request.node.get_closest_marker("setup_rates")
    if mark:
        mocker = request.getfixturevalue("mocker")
        setup_rates(mocker, **mark.kwargs)

@pytest.mark.setup_rates(return_value=Decimal(100))
def test_save_transaction():
    ...
```

@[1-3]
@[5-10]
@[12-13]

---
@snap[north]
### Async version with aiohttp
@snapend

```python
...

async def to_eur(amount, currency):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "http://127.0.0.1:5000/to_eur", 
            params={"amount": amount, "currency": currency}
        ) as response:
            data = await response.json()
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError:
                if data["detail"] == "No such rate":
                    raise NoExchangeRateError
                raise
            return Decimal(data["result"])
```

@[3-8]
@[9-16]

Note:
But what if we want to be async? No problem lets use aiohttp.

+++
@snap[north]
### Async payments
@snapend

```python
from . import exchange

async def save_transaction(booking_id, amount, currency):
    """We need to store EUR amount as well."""
    amount_eur = await exchange.to_eur(amount, currency)

    ...
```

@[3-5]

Note:
We need to adapt other code in some way.
Again, let's pretend that we work with the DB in an async way as well.

+++
@snap[north]
### Ad hoc tests
@snapend

```python
...

pytestmark = [
    pytest.mark.usefixtures("database"), 
    pytest.mark.asyncio
]

async def test_save_transaction(mocker):
    async def coro():
        return Decimal(100)

    mocker.patch(
        "booking.aio.exchange.to_eur", 
        return_value=coro()
    )
    transaction = await save_transaction(
        1, Decimal(10), "CZK"
    )
    ...

async def test_save_transaction_no_rates(mocker):
    async def coro():
        raise NoExchangeRateError("No such rate")

    mocker.patch(
        "booking.aio.exchange.to_eur", 
        return_value=coro()
    )
    with pytest.raises(
        NoExchangeRateError,
        message="No such rate"
    ):
        await save_transaction(1, Decimal(10), "NOK")
```

@[3-6]
@[8]
@[9-10]
@[12-15]
@[16-19]
@[22-23]
@[25-28]
@[29-33]

#### pytest-asyncio

+++
@transition[none]

<div class="north-west span-45" style="padding-top: 150px;">
<img src="articles/testing-network-interactions-in-python/img/pros.png" alt="Pros" width="130px" height="130px"/>
<br>
<ul>
    <li>Easy to setup</li>
    <li>Flexible</li>
</ul>
</div>

<div class="north-east span-45" style="padding-top: 150px;">
<img src="articles/testing-network-interactions-in-python/img/cons.png" alt="Cons" width="130px" height="130px"/>

<br>
<ul>
    <li>Becomes messy fast</li>
    <li>Doesn't actually test API wrapper</li>
</ul>
</div>

Note:
These kind of tests are good if you can afford to say - I don't care what this code part does internally, 
I just assume that it should return this data in this situation.
I only check if other code works if this part will provide this interface.
It could work for small and simple parts from time to time, or it could work as a temporary solution.
But usually, you can't afford yourself this level of confidence in the code

---
@snap[north]
### Generic libs
@snapend

#### Responses 
https://github.com/getsentry/responses

#### pytest-responses 
https://github.com/getsentry/pytest-responses

+++
@snap[north]
### Generic libs
@snapend

```python
def test_save_transaction(responses):
    responses.add(
        responses.GET, 
        "http://127.0.0.1:5000/to_eur", 
        body='{"result": "100"}'
    )
    ...
```

#### Responses + pytest

+++
@snap[north]
### Emulate exception
@snapend

```python
def test_save_transaction_exception(responses):
    responses.add(
        responses.GET, 
        "http://127.0.0.1:5000/to_eur", 
        body=requests.ConnectionError("Error")
    )
    ...
```

+++
@snap[north]
### Dynamic responses
@snapend

```python
...

RATES = {"CZK": Decimal("25.5")}

@pytest.fixture
def setup_rates(responses):
    def request_callback(request):
        parsed = urlparse(request.url)
        query_string = dict(parse_qsl(parsed.query))
        amount = Decimal(query_string["amount"])
        currency = query_string["currency"]
        try:
            rate = RATES[currency]
            result = {"result": format(amount / rate, ".2f")}
            status = 200
        except KeyError:
            result = {"detail": "No such rate"}
            status = 400
        return status, {}, json.dumps(result)

    responses.add_callback(
        responses.GET, 
        "http://127.0.0.1:5000/to_eur", 
        callback=request_callback
    )

@pytest.mark.usefixtures("setup_rates")
def test_save_transaction_dynamic():
    ...
```

@[5-6]
@[7-11]
@[12-19]
@[21-25]
@[27]

+++
@transition[none]

<div class="north-west span-45" style="padding-top: 150px;">
<img src="articles/testing-network-interactions-in-python/img/pros.png" alt="Pros" width="130px" height="130px"/>
<br>
<ul>
    <li>Feature-rich</li>
    <li>Well-supported</li>
</ul>
</div>

<div class="north-east span-45" style="padding-top: 150px;">
<img src="articles/testing-network-interactions-in-python/img/cons.png" alt="Cons" width="130px" height="130px"/>

<br>
<ul>
    <li>Requests - only</li>
</ul>
</div>

---
@snap[north]
### Universal solution
@snapend

#### Pook
https://github.com/h2non/pook

+++
@snap[north]
### Universal solution
@snapend

```python
@pytest.fixture
def pook():
    import pook

    pook.on()

    yield pook
    pook.off()
```

#### Pook

+++
@snap[north]
### Sync examples
@snapend

```python
...

def test_save_transaction(pook):
    pook.get(
        "http://127.0.0.1:5000/to_eur", 
        response_json={"result": 100}
    )
    ...

def test_save_transaction_no_rates(pook):
    pook.get(
        "http://127.0.0.1:5000/to_eur", 
        response_json={"detail": "No such rate"}, 
        response_status=400
    )
    ...
```
@[3-7]
@[10-15]

+++
@snap[north]
### Async examples
@snapend

```python
...

pytestmark = [
    pytest.mark.usefixtures("database"), 
    pytest.mark.asyncio
]

async def test_save_transaction(pook):
    pook.get(
        "http://127.0.0.1:5000/to_eur", 
        response_json={"result": 100}
    )
    ...

async def test_save_transaction_no_rates(pook):
    pook.get(
        "http://127.0.0.1:5000/to_eur", 
        response_json={"detail": "No such rate"}, 
        response_status=400
    )
    ...
```

@[3-6]
@[8-12]
@[15-20]

+++
@snap[north]
### More features
@snapend

- Regex matching of headers, query string, path, body, etc
- Response delay (aiohttp only)
- Callbacks
- Many more!

+++
@transition[none]

<div class="north-west span-45" style="padding-top: 150px;">
<img src="articles/testing-network-interactions-in-python/img/pros.png" alt="Pros" width="130px" height="130px"/>
<br>
<ul>
    <li>Feature-rich</li>
    <li>Works with requests, urllib3, urllib, http-client, aiohttp</li>
</ul>
</div>

<div class="north-east span-45" style="padding-top: 150px;">
<img src="articles/testing-network-interactions-in-python/img/cons.png" alt="Cons" width="130px" height="130px"/>

<br>
<ul>
    <li>Doesn't support aiohttp > 3</li>
</ul>
</div>

---
@snap[north]
### Generic libs summary
@snapend

@transition[none]

<div class="north-west span-45" style="padding-top: 150px;">
<img src="articles/testing-network-interactions-in-python/img/pros.png" alt="Pros" width="130px" height="130px"/>
<br>
<ul>
    <li>Convenient API for certain use-cases</li>
    <li>Multiple requests</li>
</ul>
</div>

<div class="north-east span-45" style="padding-top: 150px;">
<img src="articles/testing-network-interactions-in-python/img/cons.png" alt="Cons" width="130px" height="130px"/>

<br>
<ul>
    <li>Sometimes requires more manual work</li>
</ul>
</div>

---
@snap[north]
### Cassettes
@snapend

<img src="articles/testing-network-interactions-in-python/img/vhs.jpg" alt="VHS" height="400px"/>

+++
@snap[north]
### Cassettes
@snapend

#### VCR-Py 
https://github.com/kevin1024/vcrpy

#### pytest-vcr
https://github.com/ktosiek/pytest-vcr

+++
@snap[north]
### Example
@snapend

```python
...

pytestmark = [
    pytest.mark.usefixtures("database"), 
    pytest.mark.vcr
]

def test_save_transaction():
    transaction = save_transaction(1, Decimal(2550), "CZK")
    assert transaction.amount_eur == Decimal(100)

def test_save_transaction_no_rates():
    with pytest.raises(
        NoExchangeRateError, 
        message="No such rate"
    ):
        save_transaction(1, Decimal(10), "NOK")
```

@[3-6]
@[8-10]
@[12-17]

+++
@snap[north]
### Actual microservice
@snapend

```python
from decimal import Decimal

from flask import Flask, jsonify, request

app = Flask(__name__)

RATES = {
    "CZK": Decimal("25.5")
}

def convert(amount, currency):
    try:
        rate = RATES[currency]
        return format(amount / rate, ".2f")
    except KeyError:
        raise NoExchangeRateError

@app.route("/to_eur")
def to_eur():
    currency = request.args["currency"]
    amount = request.args["amount"]
    return jsonify({"result": convert(amount, currency)})

class NoExchangeRateError(Exception):
    status_code = 400

@app.errorhandler(NoExchangeRateError)
def handle_no_rate(error):
    response = jsonify({"detail": "No such rate"})
    response.status_code = error.status_code
    return response
```

@[1-5] Flask app
@[7-9] Sample rates
@[11-16] Rate conversion
@[18-22] App route
@[24-31] Error handling
 
+++
@snap[north]
### Cassette
@snapend

```yaml
interactions:
- request:
    body: null
    headers:
      ...
    method: GET
    uri: http://127.0.0.1:5000/to_eur?amount=10&currency=CZK
  response:
    body: {string: '{"result":"100.0"}'}
    headers:
      ...
    status: {code: 200, message: OK}
version: 1
```

@[2-7]
@[8-12]

#### cassettes/test_save_transaction.yaml

+++
@snap[north]
### Record modes
@snapend

- **`all`** - record all, never replay
- **`once`** - record if no cassette, only replay otherwise
- **`new_episodes`** - record if no cassette, replay and record new otherwise 
- **`none`** - never record, always replay

+++
@snap[north]
### Secrets filters
@snapend

- **Headers**
- **Querystring**
- **POST data**
- **Custom filters**

+++
@transition[none]

<div class="north-west span-45" style="padding-top: 150px;">
<img src="articles/testing-network-interactions-in-python/img/pros.png" alt="Pros" width="130px" height="130px"/>
<br>
<ul>
    <li>Easy to use</li>
    <li>Supports many http clients</li>
    <li>Multiple requests</li>
</ul>
</div>

<div class="north-east span-45" style="padding-top: 150px;">
<img src="articles/testing-network-interactions-in-python/img/cons.png" alt="Cons" width="130px" height="130px"/>

<br>
<ul>
    <li>No network exceptions emulation</li>
</ul>
</div>

---
### Combine these approaches!

---
## Real-life examples

---
@snap[north]
### API integration
@snapend

```python
@pytest.fixture
def mastercard():
    return MasterCardAPIClient()

@pytest.mark.vrc(record_mode="all")
async def test_create_card(mocker, mastercard):
    card = await mastercard.create_card(100, "EUR")
    assert card == {
        "amount": 100,
        "currency": "EUR",
        "number": mocker.ANY,
        "security_code": mocker.ANY,
        "holder": mocker.ANY,
    }
```

@[1-3]
@[5-14]

#### MasterCard XML API

+++
@snap[north]
### API integration
@snapend

```
from lxml import etree
from lxml.builder import E

@attr.s()
class MasterCardAPIClient:
    """API client for MasterCard XML API."""
    ...
    
    async def create_card(self, amount, currency):
        response = await self._call(
            E.CreatePurchaseRequest(
                Amount=amount,
                CurrencyCode=currency,
                ...
            ),
            ...
        )
        return {
            "amount": ...,
            ...
        }

    async def _call(self, *commands):
        """Make a call to MasterCard API."""
        payload = self.build_payload(*commands)
        response = await xml_request(
            "POST", 
            url=self.url, 
            data=payload, 
            verify_ssl=self.verify_ssl, 
            cert=self.request_pem
        )
        parsed = etree.fromstring(response._body)
        error = parsed.find("Error")
        if error is not None:
            raise MasterCardAPIError(error)
        return parsed   
```

@[1-2]
@[4-7]
@[9-21]
@[23-25]
@[26-32]
@[33-37]

#### Client class

+++
@snap[north]
### API integration process
@snapend

1. Write a test with **`all`** VCR record mode
2. Add code
3. Run test with sandbox credentials
4. Adapt code and test until it works
5. Make your assertions stronger
6. Repeat
 
---
@snap[north]
### Refactoring example
@snapend

- 2k lines of code class
- Multiple external API calls
- Tight coupling. Everything depends on the instance's state
- No tests

+++
@snap[north]
### Refactoring example
@snapend

```python
class BigScaryClass(object):

    def __init__(self, *args, **kwargs):
        # Few dozens of different attributes 
        # including mutable ones
        ...  

    def load_data(self):
        # Calls to external APIs
        # DB queries
        # Storing everything in instance attributes 
        ...
```

@[3-6]
@[8-12]

#### Target class

+++
@snap[north]
### Refactoring example
@snapend

```python
@pytest.mark.vcr()
def test_ancillaries_core():
    core = BigScaryClass("123", "test_service", "test", None)
    core.load_data()
    assert core.flights == {...}
    assert core.reservations == [...]
    assert core.segments == {...}
    assert core.passengers == {...}
```

@[1]
@[3-4]
@[5-8]

+++
@snap[north]
### Refactoring process
@snapend

- Choose code that you can run on production
- Record all network interactions for different cases
- Add detailed assertions
- Refactor and add new tests for refactored code
- Repeat until you're happy with new code
- Repeat on the higher abstraction level

+++
@snap[north]
### Refactoring example
@snapend

```python
@attr.s
class BigScaryClass:
    # Define only static attributes that are really needed
    ...

    def load_data(self):
        # Calls separate functions, 
        # that produce the same effects that the old code 
        # Storing only needed in instance attributes
        # Most of the new code is stateless 
        ...
```

@[1-4]
@[6-11]

+++
@snap[north]
### Result
@snapend

- The same high-level interface as before
- A much better internal structure
- You actually have tests

---
@snap[north]
#### How you could use these approaches?
@snapend

- Splitting monolithic apps
- API integrations in TDD style
- Fake responses of external APIs
- Refactoring of tightly-coupled code

---
@snap[north]
### Tools & repos
@snapend

#### unittest.mock
#### pytest-mock 

https://github.com/pytest-dev/pytest-mock

#### pytest-asyncio 

https://github.com/pytest-dev/pytest-asyncio

+++
@snap[north]
### Tools & repos
@snapend

#### responses 

https://github.com/getsentry/responses

#### pytest-responses 

https://github.com/getsentry/pytest-responses

#### pook 

https://github.com/h2non/pook

+++
@snap[north]
### Tools & repos
@snapend

#### VCR-Py 

https://github.com/kevin1024/vcrpy

#### pytest-vcr 

https://github.com/ktosiek/pytest-vcr

+++
@snap[north]
### Example repo
@snapend

https://github.com/Stranger6667/testing-network

---
## Thank you

- https://github.com/Stranger6667
- https://twitter.com/Stranger6667
