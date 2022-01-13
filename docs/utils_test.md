
## get json response and convert to tuple
* https://www.geeksforgeeks.org/python-convert-dictionary-to-list-of-tuples/
* https://www.delftstack.com/howto/python/dictionary-to-tuples-python/
```py
### Json de respuesta con 10 registros
import json
from src import utils

_p = utils.get_path_temp_from_report('proyeccion', '11149ef7-334c-11ec-8255-e4b97a19401a-RESPONSE.json')

with open(_p) as file:
    _json = json.load(file)
    
print(len(_json['registros']))    
print(_json)
print(_json['idDataset'], _json['resultado'], _json['mensaje'], _json['registros'])
print([ tuple(d.values()) for d in _json['registros'] ])

for i in utils.chunked_iterable(_json['registros'], 3):
    print([ tuple(d.values()) for d in i ])
    
for i in utils.chunked_iterable(_json['registros'], 3):    
    print([ (d['id'], d['mensaje']) for d in i ])



### Json de respuesta con mas de 50 mil registros
import json
from src import utils

_p = utils.get_path_temp_from_report('proyeccion', '67248097-334e-11ec-987e-e4b97a19401a-RESPONSE.json')

with open(_p) as file:
    _json = json.load(file)

print(len(_json['registros']))

for i in utils.chunked_iterable(_json['registros'], 20):    
    print([ (d['id'], d['mensaje']) for d in i ])

```
