import requests

url = "https://drive.google.com/drive/folders/14N-OsozTt10x1TAvfWYQy88mt0uz19oa"

r = requests.get(url)

print(r.status_code)

with open("drive_page.html", "w", encoding="utf-8") as f:
    f.write(r.text)

print("saved")