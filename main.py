from requests_html import HTMLSession
from lxml import html
import json
from time import sleep
import csv

usuarios_links = list()
with open('usuarios.csv', 'r', encoding="UTF-8") as csvfile:
    reader = csv.reader(csvfile, quoting=csv.QUOTE_NONE)
    for row in reader:
        usuarios_links.append(row[0])
    csvfile.close()

for url in usuarios_links:
    s = HTMLSession()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    r = s.get(url)
    r.html.render(timeout=60)
    soup = html.fromstring(r.text)
    data_profile = soup.xpath('//script[contains(text(), "formkey")]/text()')[0]
    data_profile = data_profile.replace('window.ansFrontendGlobals = window.ansFrontendGlobals || {};window.ansFrontendGlobals.earlySettings = ', '').replace('};', '}')
    data_profile = json.loads(data_profile)
    formkey = data_profile['formkey']
    uid = data_profile['rootQueryVariables']['uid']
    data_profile2 = soup.xpath('//script[contains(text(), "numPublicAnswers")]/text()')[0]
    data_profile2 = data_profile2.split('] = ')
    data_profile2 = data_profile2[1].split('window.ansFrontendGlobals')
    data_profile2 = data_profile2[0].replace('";', '"')
    data_profile2 = json.loads(json.loads(data_profile2))
    total_answers = data_profile2['data']['user']['numPublicAnswers']
    s.headers['quora-formkey'] = formkey
    s.headers['Content-Type'] = 'text/plain'
    title = soup.xpath('//title/text()')[0]

    with open(f"{title}.csv", 'w', encoding='UTF-8') as csvdata:
        cabeceras = ["Preguntas", "perfil", url]
        writer = csv.DictWriter(csvdata, fieldnames=cabeceras, lineterminator='\n')
        writer.writeheader()
        csvdata.close()
    after = 0
    rango = round(total_answers / 20)
    for i in range(rango):
        payload = {
            "queryName": "UserProfileAnswersMostRecent_RecentAnswers_Query",
            "extensions": {
               "hash": "327744c45507be2755e826f75d7aa32e9365f46ed980fa71d3478b479dbac3f1"
            },
            "variables": {
               "uid": uid,
               "first": 20,
               "after": str(after)
            }
        }
        r = s.post('https://www.quora.com/graphql/gql_para_POST?q=UserProfileAnswersMostRecent_RecentAnswers_Query', data=json.dumps(payload))
        data = r.json()
        data_preguntas = data['data']['user']['recentPublicAndPinnedAnswersConnection']['edges']
        preguntas = list()

        for pregunta in data_preguntas:
            titulo = json.loads(pregunta['node']['question']['title'])['sections'][0]['spans'][0]['text']
            preguntas.append(titulo)
        with open(f"{title}.csv", 'a', encoding='UTF-8') as csvdata:
            cabeceras = ["Preguntas", "perfil"]
            writer = csv.DictWriter(csvdata, fieldnames=cabeceras, lineterminator='\n')
            for pregunta in preguntas:
                writer.writerow({"Preguntas": pregunta})
            csvdata.close()
        after += 20
        print(f"Agregados {str(after)} en el CSV...")
        sleep(5)