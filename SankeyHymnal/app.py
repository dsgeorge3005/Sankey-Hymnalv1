from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import json
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load data files
with open(os.path.join(BASE_DIR, "hymns.json"), encoding="utf-8") as f:
    hymns = json.load(f)

with open(os.path.join(BASE_DIR, "audio_index.json"), encoding="utf-8") as f:
    audio_index = json.load(f)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search")
def search():
    query = request.args.get("q", "").lower().strip()
    results = []

    for hymn in hymns:
        if (
            query in hymn["title"].lower()
            or query == hymn["number"]
        ):
            hymn_copy = hymn.copy()

            # Calculate page ranges dynamically
            start_page = int(hymn["page"])
            end_page = start_page

            for h in hymns:
                if int(h["number"]) > int(hymn["number"]):
                    end_page = int(h["page"]) - 1
                    break

            pages = list(range(start_page, end_page + 1))
            hymn_copy["pages"] = pages

            # -------------------------------------------------------------
            # 🖼️ GENERATE WEBLINKS FOR IMAGES INSIDE THE pages2 FOLDER
            # -------------------------------------------------------------
            # This loops over your calculated page numbers and generates a 
            # safe web URL pointing to your 'static/pages2/' folder for each page.
            image_urls = []
            for p in pages:
                # Generates a path like '/static/pages2/1.png'
                img_url = url_for('static', filename=f"pages2/{p}.png")
                image_urls.append(img_url)
            
            hymn_copy["image_urls"] = image_urls
            # -------------------------------------------------------------

            # Fetch audio indexing
            hymn_copy["audio"] = audio_index.get(hymn["number"], {})

            # Append to your search results
            results.append(hymn_copy)

    return jsonify(results[:20])


@app.route("/audio/<path:filename>")
def audio(filename):
    return send_from_directory(
        os.path.join(BASE_DIR, "SANKEY Learning files"), 
        filename
    )


if __name__ == "__main__":
    app.run(debug=True)
