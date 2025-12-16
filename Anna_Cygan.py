"""
Uptime Scheduler-aplikacja, która na podstawie pliku konfiguracyjnego json
sprawdza dostępność stron
"""
import json
import os
import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

FILE_NAME = 'Anna_Cygan_config.json'


def read_file():
    """
    Funkcja odczytująca dane z pliku.
    """
    try:
        if not os.path.exists(FILE_NAME):
            raise FileNotFoundError

        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            context = json.load(f)

            today = datetime.date.today()

            timeout = context.get["timeout_seconds"]

            for day in context["days"]:
                if day.get("day") == today.isoweekday():
                    return {
                        "interval_seconds": day.get('interval_seconds'),
                        "urls": day.get('urls'),
                        "timeout": timeout
                    }

    except FileNotFoundError:
        print("File does not exist")
    else:
        print("File read successfully")

def availability_check(interval, urls, timeout):
    try:
        for url in urls:
            print(f"Checking url: {url}")
            req = Request(url, headers={"User-Agent": "MyApp/1.0"})
            with urlopen(req, timeout = timeout) as resp:
                print(resp.getcode())
                print(resp.read()[:1000].decode("utf-8"))

    except HTTPError as e:
        print("HTTPError: ", e.code, e.reason)
        print("Body: ", e.read()[:200])
    except URLError as e:
        print("URLError: ", e.reason)
    except Exception as e:
        print("Other error: ", e)
    else:
        print("Availability check done successfully")

schedu