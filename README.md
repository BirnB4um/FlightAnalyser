# FlightAnalyser
Ein einfacher Fluganalysator, welcher .igc Dateien einließt, sortiert und filtert.  
Gebe "help" in die Konsole ein um das Hilfemenü auszugeben.  
Alle .igc Dateien müssen im Ordner "Flights" sein (es werden auch Unterordner durchsucht).  
Flüge die kürzer als 5 Minuten sind werden automatisch rausgefiltert.  
Bei Programmstart wird eine Excelliste ("Alle_Flugdaten.xlsx") erstellt, welche jeden Flug, sortiert nach Zeit, enthält.  

Bei fehlenden Modulen:  
```
pip install -r requirements.txt
```
