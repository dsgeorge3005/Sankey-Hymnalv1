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

            # -------------------------------------------------------------
            # 📐 PAGE-RANGE CALCULATION ENGINE
            # -------------------------------------------------------------
            try:
                start_page = int(hymn["page"])
                end_page = start_page

                # Look ahead to determine where this hymn's sheet pages cut off
                for h in hymns:
                    if int(h["number"]) > int(hymn["number"]):
                        end_page = int(h["page"]) - 1
                        break

                # Guardrail: If calculation runs backward or gaps over 5 pages, clamp it
                if end_page < start_page or (end_page - start_page) > 5:
                    end_page = start_page

                pages = list(range(start_page, end_page + 1))
            except (ValueError, KeyError, TypeError):
                # Emergency structure fallback
                pages = [hymn.get("page", hymn["number"])]

            # -------------------------------------------------------------
            # 🖼️ TWO-FOLDER MULTI-PATH ROUTING ENGINE
            # -------------------------------------------------------------
            image_urls = []
            for p in pages:
                try:
                    page_num_int = int(p)
                except ValueError:
                    page_num_int = 0

                # Determine folder based on page threshold
                # Pages 1-1000 go to 'pages/', Pages 1001+ go to 'pages2/'
                if page_num_int <= 1000:
                    folder_target = "pages"
                else:
                    folder_target = "pages2"

                page_file = f"{folder_target}/{p}.png"
                page_path = os.path.join(BASE_DIR, "static", page_file)

                # DUAL PATH FALLBACK: If page number file is missing, try Hymn Number fallback
                if not os.path.exists(page_path):
                    # Check if the hymn number works in either folder
                    try:
                        hymn_num_int = int(hymn["number"])
                    except ValueError:
                        hymn_num_int = 0

                    hymn_folder = "pages" if hymn_num_int <= 1000 else "pages2"
                    hymn_num_file = f"{hymn_folder}/{hymn['number']}.png"
                    hymn_num_path = os.path.join(BASE_DIR, "static", hymn_num_file)
                    
                    if os.path.exists(hymn_num_path):
                        page_file = hymn_num_file

                img_url = url_for('static', filename=page_file)
                image_urls.append(img_url)
            
            hymn_copy["image_urls"] = image_urls
            # -------------------------------------------------------------

            # Fetch audio indexing
            hymn_copy["audio"] = audio_index.get(hymn["number"], {})

            # Append to search results layout window
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
