import requests

url = "http://sankeyhymnal.s3-website-ap-southeast-1.amazonaws.com/sankey/js/hymn-autocomplete.js"

r = requests.get(url)

print(r.status_code)

with open("hymn-autocomplete.js", "w", encoding="utf-8") as f:
    f.write(r.text)

print("saved")