"""
Uptime Scheduler-aplikacja, która na podstawie pliku konfiguracyjnego json
sprawdza dostępność stron
"""
import json
import os
import datetime
import time
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

            timeout = context["timeout_seconds"]

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
    while True:
        for url in urls:
            try:
                print(f"<{datetime.datetime.now()}>")
                print(f"Checking url: {url["url"]}")
                req = Request(url["url"], headers={"User-Agent": "MyApp/1.0"})
                start_time = time.perf_counter()
                with urlopen(req, timeout = timeout) as resp:
                    code = resp.getcode()
                    if 200 <= code < 300:
                        print("Replay: OK")
                    elif 300 <= code < 400:
                        print("Replay: Redirected")
                    elif 400 <= code < 500:
                        print("Replay: Error with query")
                    elif 500 <= code < 600:
                        print("Replay: Server error")
                end_time = time.perf_counter()
                print(f"Response time: {round(end_time-start_time,3)}s")

            except HTTPError as e:
                print("HTTPError: ", e.code, e.reason)
                print("Body: ", e.read()[:200])
            except URLError as e:
                print("URLError: ", e.reason)
            except Exception as e:
                print("Other error: ", e)
            else:
                print("Availability check done successfully")
            finally:
                print()
        print(f"Waiting {interval} seconds...\n")
        time.sleep(interval)

def main():
    info = read_file()
    availability_check(info["interval_seconds"], info["urls"], info["timeout"])


if __name__ == '__main__':
    main()

