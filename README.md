Python Library for the Bananatag API
==================================

### Usage

#### Get All Tags Within a Range
```python
from btapi.btapi import BTagAPI

btag = BTagAPI('your AuthID', 'your Access Key', debug=False);

params = {'start':'2013-09-01', 'end':'2013-09-25'}

data = btag.send('tags', params)
```

### License
Licensed under the MIT License.