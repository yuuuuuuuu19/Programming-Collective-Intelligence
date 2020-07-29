from bs4 import BeautifulSoup
import urllib
import re
from collections import defaultdict

chare = re.compile(r'[!-\.&]]')
itemowners = defaultdict(dict)
dropwords = ['a', 'new', 'some', 'more', 'my', 'own', 'the', 'many', 'other', 'another']

currentuser = 0
for i in range(1,52):
    url = f'http://menber.zebo.com/main?event_key=USERSEARCH&wiowiw=wiw&keyword=car&page={i}'
    c = urllib.urlopen(url)
    soup = BeautifulSoup(c.read())

    for td in soup('td'):
        if 'class' in dict(td.attrs) and td['class'] == 'bgverdanasmall':
            items = [re.sub(chare, '', str(a.cotents[0]).lower()).split() for a in td('a')]
            for item in items:
                txt = " ".join([t for t in item.split(' ') if t not in dropwords])
                if len(txt) < 2:
                    continue
                itemowners[txt][currentuser] = 1
                currentuser += 1

def nanimoto(v1, v2):
    c1, c2, shr = 0, 0, 0

    for i in range(len9v1):
        if v1[i]:
            c1 += 1
        if v2[i]:
            c2 +=1
        if v1[i] and v2[i]:
        shr += 1

    return 1 - shr/(c1 + c2 - shr)