#! /usr/bin/python

from datetime import datetime
import jinja2
import yaml
import pandas as pd
import requests

from envelopes import Envelope

mailing_list = [('michaelaquilina@gmail.com', 'Michael Aquilina')]

# Line for which to retrieve the status
lines = ['jubilee', 'bakerloo', 'metropolitan', 'circle', 'hammersmith-city']

detail = True

# http://api.tfl.gov.uk/
r = requests.get('http://api.tfl.gov.uk/line/{}/Status?detail={}'.format(','.join(lines), detail))

disruptions = []

if r.ok:
    data = pd.DataFrame(r.json(), columns=['id', 'name', 'lineStatuses'])
    data['status'] = ''
    data['statusSeverity'] = 0
    data['disruption'] = ''
    data.set_index('id', inplace=True)

    for index, status in data['lineStatuses'].iteritems():
        data['status'].ix[index] = status[0]['statusSeverityDescription']
        data['statusSeverity'].ix[index] = status[0]['statusSeverity']

        if 'disruption' in status[0]:
            data.ix[index]['disruption'] = status[0]['disruption']['category']
            disruptions.append(status[0]['disruption']['description'])

    del data['lineStatuses']
    print data

    t = jinja2.Template('''
        <h3>The Tube Status for {{ today.strftime('%A %d %B %Y') }}</h3>
        <table style="border: 1px solid #555555; width: 500px">
            <tr style="color: #ffffff; padding: 3px; background-color: #555555">
                <th>Line</th>
                <th>Status</th>
                <th>Details</th>
            </tr>
            {% for index, row in data.iterrows() %}
            <tr style="color: {{'green' if row.statusSeverity == 10 else 'red'}}">
                <td>{{ row['name'] }}</td>
                <td>{{ row['status'] }}</td>
                <td>{{ row['disruption'] }}</td>
            </tr>
            {% endfor %}
        </table>
        {% if disruptions %}
            <h3>Disruptions</h3>
            {% for d in disruptions %}
                <p>{{ d }}</p>
            {% endfor %}
        {% endif %}
    ''')

    env = Envelope(
        to_addr=mailing_list,
        from_addr=('my.tube.notifier@gmail.com', 'Tube Notifier'),
        subject='Today\'s Tube Status',
        html_body=t.render(data=data, today=datetime.now(), disruptions=disruptions)
    )

    config = yaml.load(open('config.yml'))
    env.send(**config)
else:
    print 'Error obtaining necessary data'
