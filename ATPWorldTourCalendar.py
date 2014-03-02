from bs4 import BeautifulSoup
import urllib.request

import re
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import time

baseurl = 'http://www.atpworldtour.com'
url = baseurl + '/Tournaments/Event-Calendar.aspx'


# get the tournament details
def gettournamentdetails(url):
    response = urllib.request.urlopen(url)
    htmlcontent = response.read()

    bs = BeautifulSoup(htmlcontent)

    divs = bs.find_all('div')
    for div in divs:
        if (div.get('id') == 'tournDetailHeadInfo'):
            listitems = div.find_all('li')
            for li in listitems:
                if 'Date:' in li.text:
                    return dict(duration=li.text, desctext=div.text)
    return None

# function returning the parsed tournament row
def gettournament(cells):
    img =  cells[0].find('img')
    if img != None:
        tournamenttype = img.get('title')  # get the image element and read the title
    else:
        tournamenttype = ""

    tournamentstartdate = cells[1].text
    tournamenttitle = cells[2].text

    tournamenttitle = tournamenttitle.replace("\n", " ")
    tournamenttitle = ' '.join(tournamenttitle.split())

    link = cells[2].find('a')
    tournamentlink = link.get('href')

    completelink = baseurl + tournamentlink

    tournament = dict(type=tournamenttype.strip(),
                      startdate=tournamentstartdate.strip(),
                      enddate=tournamentstartdate,
                      title=tournamenttitle.strip(),
                      link=completelink,
                      description='')
    return tournament





response = urllib.request.urlopen(url)
htmlcontent = response.read()


bs = BeautifulSoup(htmlcontent)

data = []
print('Load general tournament infos\n')
alltables = bs.find_all('table')
for item in alltables:
    tablerows = item.find_all('tr')
    for row in tablerows:
        classname = row.get('class')
        if classname == None:
            continue
        if classname[0] == 'calendarFilterItem':
            cells = row.find_all('td')
            if (len(cells) == 8):
                tournament = gettournament(cells)

                data.append(tournament)

print('Load specific informations\n')
# adding the correct start/enddate
i = 0
numel = len(data)
for item in data:
    if (i % 10 == 0):
        print('Loaded specific informations for {}/{} tournaments'.format(i, numel))
    z = item['link']
    details = gettournamentdetails(z)

    duration = details['duration']

    match = re.findall(r"\b([0-9]{1,2}).([0-9]{1,2}).([0-9]{4})\b", duration)
    if (len(match) == 2):
        item['startdate'] = match[0]
        item['enddate'] = match[1]
    item['description'] = details['desctext']
    i = i + 1



print('Write Calendar\n')

# creating the calendar


cal = Calendar()
cal.add('prodid', 'ATPWorldRanking')
cal.add('version', '2.0')

for item in data:
    event = Event()
    st = item['startdate']
    ed = item['enddate']

    event.add('summary', item['title'])
    event.add('dtstart', datetime(int(st[2]), int(st[1]), int(st[0]), 0, 0, 0, tzinfo=pytz.UTC))
    event.add('dtend', datetime(int(ed[2]), int(ed[1]), int(ed[0]), 0, 0, 0, tzinfo=pytz.UTC))
    event.add('dtstamp', datetime(int(time.strftime('%Y')),
                        int(time.strftime('%m')),
                        int(time.strftime('%d')),
                        int(time.strftime('%H')),
                        int(time.strftime('%M')),
                        int(time.strftime('%S')), tzinfo=pytz.UTC))
    event.add('description', item['description'].strip())

    event.add('priority',5)

    cal.add_component(event)


f = open('example.ics', 'wb')
f.write(cal.to_ical())
f.close()


print('Finished')