py-orsr
=======

Parser Obchodného registra SR (orsr.sk) pre Python. 

Parser získava z orsr.sk tieto informácie:

- názov spoločnosti
- sídlo spoločnosti
- IČO
- deň zápisu
- právna forma
- predmet činností
- spoločníci
- štatutárny orgán
- dozorná rada

# Príklady použitia

**Hľadaj spoločnosť podľa identifikačného čísla IČO**
```python
detail = orsr.OrSr().hladaj_podla_ico('45 947 597')                    
self.assertIsNotNone(detail)                                           
self.assertEqual(detail['ico'], '45 947 597')                          
self.assertEqual(detail['nazov'], 'Google Slovakia, s. r. o.') 
```

**Hľadaj spoločnosť podľa názvu**
```python
detail = orsr.OrSr().hladaj_podla_nazvu('ESET, spol. s r.o.')          
self.assertIsNotNone(detail)                                           
self.assertEqual(detail['ico'], '31 333 532')                          
self.assertEqual(detail['nazov'], 'ESET, spol. s r.o.')
```

# Inštalácia
```pip install -r requirements.txt```

# Testy
Testy sa dajú spustiť pomocou príkazu: 

```python -m unittest test_orsr_parser.py```
