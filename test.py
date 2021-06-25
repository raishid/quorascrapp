from requests_html import HTMLSession
from lxml import html
import json
import csv
from time import sleep
import traceback

after = 9740
uid = 472
url = 'https://www.quora.com/profile/Marc-Bodnick'
has_next_page = True
try:
    while has_next_page:
        s = HTMLSession()
        s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        r = s.get(url)
        r.html.render(timeout=60)
        soup = html.fromstring(r.text)
        data_profile = soup.xpath('//script[contains(text(), "formkey")]/text()')[0]
        data_profile = data_profile.replace('window.ansFrontendGlobals = window.ansFrontendGlobals || {};window.ansFrontendGlobals.earlySettings = ','').replace('};', '}')
        data_profile = json.loads(data_profile)
        formkey = data_profile['formkey']
        uid = data_profile['rootQueryVariables']['uid']
        data_profile2 = soup.xpath('//script[contains(text(), "numPublicAnswers")]/text()')[0]
        data_profile2 = data_profile2.split('] = ')
        data_profile2 = data_profile2[1].split('window.ansFrontendGlobals')
        data_profile2 = data_profile2[0].replace('";', '"')
        data_profile2 = json.loads(json.loads(data_profile2))
        total_answers = data_profile2['data']['user']['numPublicAnswers']
        total_questions = data_profile2['data']['user']['numProfileQuestions']
        s.headers['quora-formkey'] = formkey
        s.headers['Content-Type'] = 'text/plain'
        title = soup.xpath('//title/text()')[0]

        payload = {
            "queryName": "UserProfileQuestions_Questions_Query",
            "extensions": {
                "hash": "83aef3e5f1e12333e2b35ad1f55f18efe367eecda053ab5f8d9d62d93f6f7269"
            },
            "variables": {
                "uid": uid,
                "first": 20,
                "after": str(after)
            }
        }
        r = s.post('https://www.quora.com/graphql/gql_para_POST?q=UserProfileQuestions_Questions_Query', data=json.dumps(payload))
        data = r.json()
        data_preguntas = data['data']['user']['recentPublicQuestionsConnection']['edges']
        siguiente_pagina = data['data']['user']['recentPublicQuestionsConnection']['pageInfo']['endCursor']
        has_next_page = data['data']['user']['recentPublicQuestionsConnection']['pageInfo']['hasNextPage']
        preguntas = list()
        for pregunta in data_preguntas:
            titulo = json.loads(pregunta['node']['title'])['sections'][0]['spans'][0]['text']
            preguntas.append(titulo)
        with open(f"{title}.csv", 'a', encoding='UTF-8') as csvdata:
            cabeceras = ["Preguntas", "perfil"]
            writer = csv.DictWriter(csvdata, fieldnames=cabeceras, lineterminator='\n')
            for pregunta in preguntas:
                writer.writerow({"Preguntas": pregunta})
            csvdata.close()
        if has_next_page:
            after = siguiente_pagina
            print(f"Agregados {str(after)} en el CSV...")
            open("acciones_continuaciones.log", 'a', encoding='utf-8').writelines(f"Agregados {str(after)} en el CSV...\n")
            sleep(5)
except:
    error = traceback.format_exc()
    open("error2.log", 'a', encoding="UTF-8").writelines(f"{error}\n")


