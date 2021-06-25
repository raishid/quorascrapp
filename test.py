import csv
usuarios_links = list()
with open('usuarios.csv', 'r', encoding="UTF-8") as csvfile:
    reader = csv.reader(csvfile, quoting=csv.QUOTE_NONE)
    for row in reader:
        usuarios_links.append(row[0])
    csvfile.close()

print(usuarios_links)