import requests
import sqlite3

def extract(fromDate, toDate):
    # Extract data from API of the central production Hawes
    # fromDate and toData are "DD-MM-YYYY" strings

    url = "https://interview.beta.bcmenergy.fr/hawes?from=" + fromDate + "&to=" + toDate
    response = requests.get(url)

    if response:
        content = response.json()
        return content
    else:
        print("An error has occured from the API !")
        return []
        
def transform(datas):
    # Transform datas in the right format 
    # datas is a list of {'start': timestamp, 'end': timestamp, 'power': int} dictionnaries

    new_datas = []
    if len(datas) != 0:

        last_end_date = datas[0]["end"]
        new_datas.append(datas[0])
        
        for i in range(1, len(datas)):

            current_start_date = datas[i]["start"]

            # Test to add a new value if there is a missing value in the dataset
            if current_start_date != last_end_date:
                # Creation of the new value
                new_power_to_add = int((datas[i-1]['power']+datas[i]['power'])/2)
                new_datas.append({'start': last_end_date, 'end': current_start_date, 'power': new_power_to_add})

            new_datas.append(datas[i])
            last_end_date = datas[i]["end"]

    return new_datas

def upload(datas):
    # Upload datas on the database 
    # datas is a list of {'start': timestamp, 'end': timestamp, 'power': int} dictionnaries

    if len(datas) != 0:

        # Connecting to sqlite
        sqliteConnection = sqlite3.connect('db.sqlite')
        cursor = sqliteConnection.cursor()

        # Insert datas
        for data in datas:
            query = "INSERT INTO energyProduction (start_date, power) VALUES ("+ str(data["start"]) +", " + str(data["power"]) + ");"
            cursor.execute(query)
        
        # Commit and close connexion
        sqliteConnection.commit()
        sqliteConnection.close()

datas = extract("01-01-2016", "01-01-2017")
new_datas = transform(datas)
upload(new_datas)
