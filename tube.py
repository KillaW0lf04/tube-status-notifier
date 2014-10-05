import pandas as pd
import requests

# Line for which to retrieve the status
lines = ['jubilee', 'bakerloo', 'metropolitan', 'circle', 'hammersmith-city']

r = requests.get('http://api.tfl.gov.uk/line/{}/Status?'.format(','.join(lines)))

if r.ok:
    data = pd.DataFrame(r.json(), columns=['id', 'name', 'lineStatuses'])
    data['Status'] = ''
    data['Category'] = ''
    data.set_index('id', inplace=True)

    for index, status in data['lineStatuses'].iteritems():
        data.ix[index]['Status'] = status[0]['statusSeverityDescription']

        if 'disruption' in status[0]:
            data.ix[index]['Category'] = status[0]['disruption']['category']

    del data['lineStatuses']
    print data
else:
    print 'Error obtaining necessary data'
