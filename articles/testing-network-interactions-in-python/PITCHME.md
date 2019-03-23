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
