#! /usr/bin/python

from datetime import datetime
import jinja2
import yaml
import pandas as pd
import requests

from envelopes import Envelope

config = yaml.load(open('config.yml'))

# Load Configuration Options
lines = config['lines']
mail_to = config['mail_to']
mail = config['mail']

detail = True

# http://api.tfl.gov.uk/
r = requests.get('http://api.tfl.gov.uk/line/{}/Status?detail={}'.format(','.join(lines), detail))

reasons = []

if r.ok:
    data = pd.DataFrame(r.json(), columns=['id', 'name', 'lineStatuses'])
    data['status'] = ''
    data['statusSeverity'] = 0
    data.set_index('id', inplace=True)

    for index, status in data['lineStatuses'].iteritems():
        data['status'].ix[index] = status[0]['statusSeverityDescription']
        data['statusSeverity'].ix[index] = status[0]['statusSeverity']

        reasons.append(status[0].get('reason', ''))

    del data['lineStatuses']
    print data

    t = jinja2.Template('''
        <h3>The Tube Status for {{ today.strftime('%A %d %B %Y') }}</h3>
        <table style="border: 1px solid #555555; width: 500px">
            <tr style="color: #ffffff; padding: 3px; background-color: #555555">
                <th>Line</th>
                <th>Status</th>
                <th>Severity</th>
            </tr>
            {% for index, row in data.iterrows() %}
            <tr style="color: {{'green' if row.statusSeverity == 10 else 'red'}}">
                <td>{{ row['name'] }}</td>
                <td>{{ row['status'] }}</td>
                <td>{{ row['statusSeverity'] }}</td>
            </tr>
            {% endfor %}
        </table>
        {% if reasons %}
            <h3>Details</h3>
            {% for r in reasons %}
                <p>{{ r }}</p>
            {% endfor %}
        {% endif %}
    ''')

    env = Envelope(
        to_addr=mail_to,
        from_addr=('my.tube.notifier@gmail.com', 'Tube Notifier'),
        subject='Today\'s Tube Status',
        html_body=t.render(data=data, today=datetime.now(), reasons=reasons)
    )

    env.send(**mail)
else:
    print 'Error obtaining necessary data'
