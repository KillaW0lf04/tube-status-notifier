import pandas as pd
import requests
import yaml

from envelopes import Envelope

mailing_list = [('michaelaquilina@gmail.com', 'Michael Aquilina')]

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

    env = Envelope(
        to_addr=mailing_list,
        from_addr=('my.tube.notifier@gmail.com', 'Tube Notifier'),
        subject='Today\'s Tube Status',
        html_body=data.to_html()
    )

    config = yaml.load(open('config.yml'))
    env.send(**config)
else:
    print 'Error obtaining necessary data'
