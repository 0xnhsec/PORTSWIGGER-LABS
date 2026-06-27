# code from rana khalil
print("[", end='')

with open('PS-wordlists/password/PS-P-L.lst', 'r') as f:
    lines = f.readlines()

for pwd in lines:
    print('"' + pwd.rstrip('\n') + '",', end='')

print('"random"]', end='')
