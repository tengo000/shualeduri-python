import datetime
import json
import sqlite3

import requests
from requests import api

country = input("Text a country: ")


class CovidStats:
    URL = f"https://api.covid19api.com/country/{country}?from=2021-05-01T00:00:00Z&to=2021-05-10T00:00:00Z"
    new_date_format = "%d-%m-%y"

    def __init__(self):
        pass

    @staticmethod
    def _load_json_data(url):
        covid_data = requests.get(url)
        if 200 <= covid_data.status_code < 300:
            return covid_data.json()
        else:
            print(f"Error with status code: {covid_data.status_code}")

    def load_into_database(self, table_name, con, cur):
        covid_data = self._load_json_data(self.URL)
        for covid_stat in covid_data:
            date = covid_stat['Date']
            d1 = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
            new_date = d1.strftime(self.new_date_format)
            cur.execute(
                f"INSERT INTO {table_name} VALUES('{new_date}', {covid_stat['Confirmed']}, {covid_stat['Recovered']}, {covid_stat['Deaths']}, {covid_stat['Active']})")
            con.commit()

    def print_covid_stats(self):
        load_covid_stats = self._load_json_data(self.URL)
        for i in load_covid_stats:
            date = i['Date']
            d1 = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
            new_date = d1.strftime(self.new_date_format)
            print('თარიღი:', new_date)
            print(' კოვიდის დადასტურებული შემთხვევა:', i['Confirmed'])
            print('გამოჯანმრთელებული რაოდენობა:', i['Recovered'])
            print('გარდაცვლილთა ოდენობა:', i['Deaths'])
            print('აქტიური:', i['Active'])
            print()

    @staticmethod
    def _save_to_disc(filename, data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    def load_data_to_json(self):
        results = self._load_json_data(self.URL)
        self._save_to_disc("covid-stats.json", results)


def create_table(con):
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS covid(d_date TEXT, cases INTEGER, recovered INTEGER, deaths INTEGER, active INTEGER)")
    con.commit()


def main(con):
    create_table(con)


if _name_ == "_main_":
    connection = sqlite3.connect("covid-stats.db")
    cursor = connection.cursor()
    main(connection)
    covid_stats = CovidStats()
    covid_stats.print_covid_stats()
    covid_stats.load_data_to_json()
    covid_stats.load_into_database("covid", connection, cursor)

#api.covid19api.com
