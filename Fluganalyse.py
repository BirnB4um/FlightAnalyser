from aerofiles.igc import Reader
from pathlib import Path
import datetime as dt
import math
import os
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


#variables
MINIMUM_FLIGHT_LENGTH = 5 * 60

all_flights = []
sorted_flights = []
filtered_flights = {}
filtered_flights_string = ""
all_places = []

def cls():
    os.system("cls")


def time_to_seconds(time):#takes dt.time parameter
    return ((time.hour * 60) + time.minute) * 60 + time.second


def get_flight(file=""):
    if file == "":
        return -1

    with open(file, 'r') as f:
        parsed_igc_file = Reader().read(f)

    data = {}
    data["flight_number"] = 0
    data["date"] = parsed_igc_file["header"][1]["utc_date"]
    data["place"] = parsed_igc_file["header"][1]["site"]
    data["start_time"] = parsed_igc_file["fix_records"][1][0]["time"]
    data["end_time"] = parsed_igc_file["fix_records"][1][-1]["time"]
    data["duration"] = time_to_seconds(data["end_time"]) - time_to_seconds(data["start_time"])
    data["flight_points"] = {
        "timestamp" : [ d["time"] for d in parsed_igc_file["fix_records"][1]],
        "positions" : [ [d["lat"], d["lon"]] for d in parsed_igc_file["fix_records"][1]],
        "pressure_altitude" : [ d["pressure_alt"] for d in parsed_igc_file["fix_records"][1]],
        "gps_altitude" : [ d["gps_alt"] for d in parsed_igc_file["fix_records"][1]]
    }
    return data


def get_flight_string(flight):
    temp = flight["flight_number"]
    number = f"{temp:04}."
    date = flight["date"].strftime("%d/%m/%Y")
    place = "Ort: " + flight["place"]
    start_time = flight["start_time"].strftime("Start: %H:%M:%S Uhr")

    sec = flight["duration"]
    min = math.floor(sec/60)
    sec = sec % 60
    hours = math.floor(min/60)
    min = min % 60
    duration = f"Dauer: {hours:02}:{min:02}:{sec:02}"

    string = f"{number}  {date}   {start_time}   {duration}   {place}"
    return string


def filter_by_place(target_place):
    global filtered_flights
    filtered_flights = {}

    for flight in sorted_flights:
        if flight["place"] == target_place:
            place = flight["place"]
            year = str(flight["date"].year)
            month = flight["date"].strftime("%B")
            day = str(flight["date"].day)

            if not place in filtered_flights.keys():
                filtered_flights[place] = {}
            
            if not year in filtered_flights[place].keys():
                filtered_flights[place][year] = {}

            if not month in filtered_flights[place][year].keys():
                filtered_flights[place][year][month] = {}

            if not day in filtered_flights[place][year][month].keys():
                filtered_flights[place][year][month][day] = []
            
            filtered_flights[place][year][month][day].append(get_flight_string(flight))


def filter_by_year(target_year):
    global filtered_flights
    filtered_flights = {}

    for flight in sorted_flights:
        if flight["date"].year == target_year:
            year = str(flight["date"].year)
            month = flight["date"].strftime("%B")
            day = str(flight["date"].day)

            if not year in filtered_flights.keys():
                filtered_flights[year] = {}

            if not month in filtered_flights[year].keys():
                filtered_flights[year][month] = {}

            if not day in filtered_flights[year][month].keys():
                filtered_flights[year][month][day] = []
            
            filtered_flights[year][month][day].append(get_flight_string(flight))


def filter_by_all():
    global filtered_flights
    filtered_flights = {}

    for flight in sorted_flights:
        year = str(flight["date"].year)
        month = flight["date"].strftime("%B")
        day = str(flight["date"].day)

        if not year in filtered_flights.keys():
            filtered_flights[year] = {}

        if not month in filtered_flights[year].keys():
            filtered_flights[year][month] = {}

        if not day in filtered_flights[year][month].keys():
            filtered_flights[year][month][day] = []
        
        filtered_flights[year][month][day].append(get_flight_string(flight))


def print_filtered_flights():
    global filtered_flights_string

    print("\nFlugliste:")
    filtered_flights_string = "Keine Daten!"

    if len(filtered_flights.keys()) == 0:
        print(filtered_flights_string)
        return

    def get_dict_tree(data, indent=""):
        result = ""
        keys = list(data.keys())
        for i, key in enumerate(keys):
            if i == len(keys) - 1:
                arrow = "└─"
                next_indent = indent + "  "
            else:
                arrow = "├─"
                next_indent = indent + "│ "
            result += indent + arrow + key + "\n"
            if isinstance(data[key], dict):
                result += get_dict_tree(data[key], indent=next_indent)
            else:
                if isinstance(data[key], list):
                    for item in data[key]:
                        if item == data[key][-1]:
                            result += next_indent + "└─" + str(item) + "\n"
                        else:
                            result += next_indent + "├─" + str(item) + "\n"
                else:
                    result += next_indent + "└─" + str(data[key]) + "\n"
        return result

    filtered_flights_string = get_dict_tree(filtered_flights)
    
    print(filtered_flights_string)
    print()


def print_help():
    print("\n === Liste aller Befehle ===")
    print("   help       -   Zeigt dieses Menü")
    print("   cls        -   Löscht den Konsoleninhalt")
    print("   exit       -   Schließt die Anwendung")
    print("   liste      -   Zeigt die aktuell gefilterte Liste an")
    print("   filter     -   Ändert Filterbedingung")
    print("   analyse    -   Analysiert einen Flug")
    print("   speichern  -   Speichert aktuell gefilterte Liste als Datei ab")
    print("   statistik  -   Generiert Statistiken aller Flüge")
    print()


def edit_filter():
    filter = ""
    while True:
        print("Mögliche Filteroptionen: Alle, Ort, Jahr")
        filter = input("Neuer Filter: ")
        if filter.lower() in ["alle", "ort", "jahr"]:
            break
        print("Ungültige Eingabe!")

    if filter.lower() == "alle":
        filter_by_all()

    elif filter.lower() == "ort":
        target_place = 0
        while True:
            print("Liste aller Orte:")
            for i in range(1, len(all_places)+1):
                print(f"    {i}. {all_places[i-1]}")
                
            target_place = input("\nGebe Nummer eines Ortes an: ")
            try:
                target_place = int(target_place)-1
            except:
                print("Ungültige Eingabe! Gebe eine NUMMER ein.")
                continue

            if target_place < 0 or target_place >= len(all_places):
                print("Ungültige Eingabe! Nummer ist nicht in der Liste. Gibt eine Nummber dieser Liste ein:")
                continue

            filter_by_place(all_places[target_place])
            break

    elif filter.lower() == "jahr":
        target_year = 0
        while True:
            target_year = input("Gebe ein Jahr an: ")
            try:
                target_year = int(target_year)
            except:
                print("Ungültige Eingabe!")
                continue
            break
        
        filter_by_year(target_year)

    print_filtered_flights()


def save_list_as_file():
    name = input("Wie soll die Datei heißen?: ").split(".")[0]
    with open(name+".txt", "w", encoding="utf-8") as file:
        file.write(filtered_flights_string)
    print("Datei wurde gespeichert")


def analyse_flight():
    number = 0
    while True:
        number = input("Gebe eine Flugnummer ein: ")
        try:
            number = int(number)-1
            if number < 0 or number >= len(sorted_flights):
                raise ValueError
            break
        except:
            print("Keine gültige Eingabe!")
            continue
    
    # print("\n === Analysedaten für folgenden Flug ===")
    # print(get_flight_string(sorted_flights[number]))

    #height diagram
    x = [dt.datetime.combine(dt.date(2023,1,1), i) for i in sorted_flights[number]["flight_points"]["timestamp"]]
    height = sorted_flights[number]["flight_points"]["pressure_altitude"]# "pressure_altitude" or "gps_altitude"
    fig, ax = plt.subplots(1)
    fig.set_size_inches(8, 6, forward=True)
    fig.autofmt_xdate()
    ax.plot(x, height, color="blue", linewidth=1)
    xfmt = mdates.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    ax.set_xlabel("Time")
    ax.set_ylabel("Höhe (meter)")
    ax.grid(True)
    plt.title(get_flight_string(sorted_flights[number]))
    fig.canvas.manager.set_window_title(str(sorted_flights[number]["flight_number"]))
    fig.tight_layout()

    plt.show()


def generate_statistics():
    print("Noch nicht implementiert. Hier würden jetzt allgemeine statistiken über alle Flüge stehen + Diagramme")
    #TODO
    #avg dauer
    #avg startzeit
    #avg dauer pro ort
    #max höhe
    #number of flights
    #
    #alle flüge: länge über zeitraum
    #diagram: startzeit der flüge
    


def on_startup():
    text = ""
    for flight in sorted_flights:
        text += get_flight_string(flight) + "\n"
    text = text[:-1]

    # with open("Alle_Flugdaten.txt", "w") as file:
    #     file.write(text)

    data = []
    for flight in sorted_flights:
        sec = flight["duration"]
        min = math.floor(sec/60)
        sec = sec % 60
        hours = math.floor(min/60)
        min = min % 60
        duration = f"{hours:02}:{min:02}:{sec:02}"
        data.append([flight["flight_number"], flight["date"].strftime('%d/%m/%Y'), flight["start_time"].strftime('%H:%M:%S'), duration, flight["place"]])
    
    df = pd.DataFrame(data, columns=["Flugnummer", "Datum", "Zeit", "Dauer", "Ort"])
    df.to_excel("Alle_Flugdaten.xlsx", sheet_name="Flugdaten", index=False)



#==========================================================================


cls()
print("Lade Daten...")

#load all flights
for path in Path('Flights').rglob('*.igc'):
    flight = get_flight(path)
    if flight["duration"] > MINIMUM_FLIGHT_LENGTH:
        all_flights.append(flight)
flight_index = [i for i in range(len(all_flights))]


#sort flights by time
for max_i in range(len(all_flights)-1, 0, -1):
    for i in range(max_i):
        if dt.datetime.combine(all_flights[flight_index[i]]["date"], all_flights[flight_index[i]]["start_time"]).timestamp() > dt.datetime.combine(all_flights[flight_index[i+1]]["date"], all_flights[flight_index[i+1]]["start_time"]).timestamp():
            temp = flight_index[i]
            flight_index[i] = flight_index[i+1]
            flight_index[i+1] = temp
n = 1
for i in flight_index:
    sorted_flights.append(all_flights[i])
    sorted_flights[-1]["flight_number"] = n
    n+=1

#make list of all places
for flight in sorted_flights:
    if not flight["place"] in all_places:
        all_places.append(flight["place"])

cls()

#filter list
filter_by_all()


on_startup()


print_help()

while True:

    user_input = input(">")
    command = user_input.lower()

    if command == "help":
        print_help()
    elif command == "exit":
        break
    elif command == "cls":
        cls()
    elif command == "liste":
        print_filtered_flights()
    elif command == "filter":
        edit_filter()
    elif command == "speichern":
        save_list_as_file()
    elif command == "analyse":
        analyse_flight()
    elif command == "statistik":
        generate_statistics()
    else:
        print("Unbekannter Befehl! Gebe 'help' ein um eine Liste aller Befehle auszugeben.")


#==========================================================================