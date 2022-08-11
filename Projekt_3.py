"""

projekt_3.py: třetí projekt do Engeto Online Python Akademie


autor: Martin Nováček

email: mnovacek@me.com

discord: Novicce #7276

"""



import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup


def process_row(row, data):
    code = row.find('td', {'class': 'cislo'})
    name = row.find('td', {'class': 'overflow_name'})
    if not code or not name: 
        return

    link = code.find('a')['href']
    code = code.string
    name = name.string

   
    request = requests.get('https://volby.cz/pls/ps2017nss/' + link)
    request.raise_for_status() 
    page = BeautifulSoup(request.text, 'html.parser')

    tables = page.findChildren('table')
    stats = tables[0]

    stats_cols = stats.findChildren('td')
    selector_cnt = str(stats_cols[3].string).replace(u'\xa0', ' ')  
    envelope_cnt = str(stats_cols[4].string).replace(u'\xa0', ' ')
    votes_cnt = str(stats_cols[7].string).replace(u'\xa0', ' ')

    parties = []
    for table in tables[1:]:  
        for party in table.findChildren('td', {'class': 'overflow_name'}):  
            parties.append(party.string)

    parties = '|'.join(parties)  
    data.append([code, name, selector_cnt, envelope_cnt, votes_cnt, parties])


def scrape_page(page, out_file):
    rows = page.findChildren('tr')  
    data = []
    for row in rows:
        process_row(row, data)

    df = pd.DataFrame(data, columns=['kód obce', 'název obce', 'voliči v seznamu', 'vydané obálky', 'platné hlasy',
                                     'kandidující strany']).set_index('kód obce')
    df.to_csv(out_file, sep=';')


def parse_args():
    try:
        link = sys.argv[1]
        request = requests.get(link)
        request.raise_for_status()
        page = BeautifulSoup(request.text, 'html.parser')
        out_file = sys.argv[2]
    except IndexError:
        raise SystemExit(f'Usage: {sys.argv[0]} <link> <output file>')
    except requests.exceptions.HTTPError:
        raise SystemExit(f'Link {sys.argv[1]} is not working')

    return page, out_file


def main():
    page, out_file = parse_args()
    scrape_page(page, out_file)


if __name__ == '__main__':
    main()
