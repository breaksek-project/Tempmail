import requests
import random
import string
import time
import re

BASE_URL = "https://api.mail.tm"

def random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# 1. Ambil domain
def get_domain():
    res = requests.get(f"{BASE_URL}/domains")
    res.raise_for_status()
    domains = res.json()["hydra:member"]
    return domains[0]["domain"]

# 2. Buat akun temp mail
def create_account(email, password="temppass123"):
    data = {"address": email, "password": password}
    res = requests.post(f"{BASE_URL}/accounts", json=data)
    if res.status_code != 201 and "exists" not in res.text:
        raise Exception("Gagal membuat akun:", res.text)

# 3. Login dan dapatkan token
def get_token(email, password="temppass123"):
    res = requests.post(f"{BASE_URL}/token", json={"address": email, "password": password})
    res.raise_for_status()
    return res.json()["token"]

# 4. Cek inbox
def check_inbox(token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/messages", headers=headers)
    res.raise_for_status()
    return res.json()["hydra:member"]

# 5. Baca isi pesan
def read_message(token, message_id):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/messages/{message_id}", headers=headers)
    res.raise_for_status()
    return res.json()

if __name__ == "__main__":
    username = random_string()
    domain = get_domain()
    email = f"{username}@{domain}"
    password = "temppass123"

    print(f"[+] Temp Mail: {email}")

    create_account(email, password)
    token = get_token(email, password)

    print("[*] Menunggu email masuk... (Tekan Ctrl+C untuk keluar)")

    try:
        while True:
            inbox = check_inbox(token)
            if inbox:
                print(f"\n[📩] Dapat {len(inbox)} email!")
                for msg in inbox:
                    print(f"From: {msg['from']['address']}")
                    print(f"Subject: {msg['subject']}")
                    detail = read_message(token, msg["id"])
                    body = detail.get('text') or '[Tidak ada isi]'
                    print(f"Body:\n{body}\n")

                    # Ekstrak link dari isi pesan jika ada
                    links = re.findall(r'https?://\S+', body)
                    if links:
                        print("[🔗] Link ditemukan:")
                        for link in links:
                            print(f"- {link}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[!] Program dihentikan oleh pengguna.")
