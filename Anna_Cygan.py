"""
Uptime Scheduler is an app, which checks the availability of websites
based on a JSON configuration file.
"""
import json
import os
import datetime
import signal
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

FILE_NAME = 'Anna_Cygan_config.json'
LOG_FILE = 'log_file.txt'

WORKING = True

def handle_sigint(_signum, _frame):
    """
    Function that handles CTRL+C to allow graceful shutdown
    """
    global WORKING
    print("Finishing iteration...")
    WORKING = False

def read_file():
    """
    Function that reads information from json file.
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
                        "timeout": timeout,
                        "log": day.get('log')
                    }
            print("No configuration found for today")
            return None

    except FileNotFoundError:
        print("File does not exist")
        return None
    except Exception as e:
        print("Other error: ", e)

def availability_check():
    """
    Function that checks the availability of websites and
    prints the results. It also passes the information to another
    two functions to translate the website code and to write
    results into the file.
    """
    while WORKING:
        info = read_file()
        response_time = '-'
        code_ans = '-'

        if info is None:
            print("Error with configuration. Waiting 5s...")
            time.sleep(5)
            continue

        interval, urls, timeout, log = info["interval_seconds"], info["urls"], info["timeout"], info["log"]
        for url in urls:
            if not WORKING:
                break
            try:
                print(f"<{datetime.datetime.now().strftime('%H:%M:%S')}>")
                print(f"Checking url: {url['url']}")
                req = Request(url['url'], headers={"User-Agent": "MyApp/1.0"})

                start_time = time.perf_counter()

                with urlopen(req, timeout = timeout) as resp:
                    code = resp.getcode()
                    code_ans = code_identification(code)
                    print(code_ans)

                end_time = time.perf_counter()

                response_time = round(end_time - start_time, 3)
                print(f"Response time: {response_time}s")

            except HTTPError as e:
                print("HTTPError: ", e.code, e.reason)
                code_ans = f"Error: {e.reason}"
                response_time = '-'
            except URLError as e:
                print("URLError: ", e.reason)
                code_ans = f"Error: {e.reason}"
                response_time = '-'
            except Exception as e:
                print("Other error: ", e)
                code_ans = f"Error: {e}"
                response_time = '-'
            finally:
                if log:
                    write_log_to_file(url = url, response_time = response_time, code_ans = code_ans)
                print("=" * 15)

        print(f"Waiting {interval} seconds...(Press Ctrl+C to stop)\n")
        try:
            time.sleep(interval)
        except OSError:
            pass

    print("Program closed.")

def code_identification(code):
    """
    This function interprets the page code into a verbal response
    """
    if 200 <= code < 300:
        return "Replay: OK"
    elif 300 <= code < 400:
        return "Replay: Redirected"
    elif 400 <= code < 500:
        return "Replay: Error with query"
    elif 500 <= code < 600:
        return "Replay: Server error"
    return f"Replay: Unknown code: {code}"

def write_log_to_file(url, code_ans, response_time):
    """
    This function writes arguments such as code answer, name of the website
    and response time (if there is no error)
    """
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        try:
            f.write(f"<{datetime.datetime.now().strftime('%H:%M:%S')}>\n"
                    f"Name: {url['url']}\n"
                    f"{code_ans}\n"
                    f"Response time: {response_time}\n"
                    f"\n")
        except IOError as e:
            print("Could not write to log file: ", e )


def main():
    """
    Main function
    """
    signal.signal(signal.SIGINT, handle_sigint)

    availability_check()

if __name__ == '__main__':
    main()

