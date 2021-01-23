import json

all_text = ''
txt_json = ''
text_json = ''
files_list = ['C:\\Объекты\\files\\2506b19a.json', 'C:\\Объекты\\files\\2506b19b.json',
              'C:\\Объекты\\files\\2506b19c.json', 'C:\\Объекты\\files\\2506b19d.json',
              'C:\\Объекты\\files\\2506b19e.json', 'C:\\Объекты\\files\\2506b19f.json',
              'C:\\Объекты\\files\\2506b19g.json', 'C:\\Объекты\\files\\2506b19h.json',
              'C:\\Объекты\\files\\2506b19i.json', 'C:\\Объекты\\files\\2506b19j.json',
              'C:\\Объекты\\files\\2506b19k.json', 'C:\\Объекты\\files\\2506b19l.json',
              'C:\\Объекты\\files\\2506b19m.json', 'C:\\Объекты\\files\\2506b19n.json']
for file_name in files_list:
    file = open(file_name, 'r', encoding='utf-8')
    txt_json = ''
    for l in file:
        txt_json = txt_json + l
    loaded_json = json.loads(txt_json)
    text_json = text_json + str(loaded_json)
    file.close()
file_w = open('C:\\Объекты\\files\\qa1.txt', 'w', encoding='utf-8')
file_w.write(text_json)
file_w.close()
