Python Library for the Bananatag API
==================================

### Usage

#### Get All Tags Within a Range
```python
from btapi.btapi import BTagAPI

btag = BTagAPI('your AuthID', 'your Access Key');

params = {'start':'2013-09-01', 'end':'2013-09-25'}

data = btag.request('tags', params)
```

### License
Licensed under the MIT License.