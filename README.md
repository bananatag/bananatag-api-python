Python Library for the Bananatag API
==================================

### Basic Usage

#### Get All Tags Within a Range
```python
from btapi.btapi import BTagAPI

btag = BTagAPI('your AuthID', 'your Access Key')

params = {'start':'2014-09-01', 'end':'2014-09-25'}

tags = btag.request('tags', params)

for tag in tags['data']:
    print 'Tag ID: {0}'.format(tag['id'])
    print 'Subject: {0}'.format(tag['subject'])
    print 'Total Opens: {0}'.format(tag['data']['totalOpens'])
    print 'Unique Opens: {0}'.format(tag['data']['uniqueOpens'])
    print 'Desktop Opens: {0}'.format(tag['data']['desktopOpens'])
    print 'Mobile Opens: {0}'.format(tag['data']['mobileOpens'])
    print 'Total Clicks: {0}'.format(tag['data']['totalClicks'])
    print 'Unique Clicks: {0}'.format(tag['data']['uniqueClicks'])
    print 'Desktop Clicks: {0}'.format(tag['data']['desktopClicks'])
    print 'Mobile Clicks: {0}'.format(tag['data']['mobileClicks'])
    print 'Date Sent: {0}'.format(tag['dateSent'])
```

#### Pagination
Each time you make a request with the same endpoint and parameters, the library automatically grabs the next page of results.
```python
import time
from btapi.btapi import BTagAPI

btag = BTagAPI('your AuthID', 'your Access Key')

while True:
    tags = btag.request('tags')

    if not data:
        break

    for tag in tags['data']:
        print tag['subject'], tag['dateSent']

    time.sleep(1)
```

### Request Limit
The API is limited to 1 request per second.

### License
Licensed under the MIT License.