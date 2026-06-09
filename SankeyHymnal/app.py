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
            # 🖼️ SANKEY SPECIFIC MULTI-FOLDER ROUTING ENGINE (.jpg)
            # -------------------------------------------------------------
            image_urls = []
            
            for p in pages:
                try:
                    page_num_int = int(p)
                except ValueError:
                    page_num_int = 0

                # 1. Determine folder based on page number threshold
                if page_num_int <= 1000:
                    folder_target = "pages"
                else:
                    folder_target = "pages2"

                # 2. Build filename matching your exact format: Sankey_[number].jpg
                filename_target = f"{folder_target}/Sankey_{page_num_int}.jpg"
                full_check_path = os.path.join(app.static_folder, filename_target)
                
                # Case-Insensitive Extension Check fallback (.jpg vs .JPG)
                if not os.path.exists(full_check_path):
                    alt_check_path = os.path.join(app.static_folder, f"{folder_target}/Sankey_{page_num_int}.JPG")
                    if os.path.exists(alt_check_path):
                        filename_target = f"{folder_target}/Sankey_{page_num_int}.JPG"
                    else:
                        # 3. Fallback to Hymn Number if page calculation falls short
                        try:
                            hymn_num_int = int(hymn["number"])
                        except ValueError:
                            hymn_num_int = 0
                        
                        hymn_folder = "pages" if hymn_num_int <= 1000 else "pages2"
                        filename_target = f"{hymn_folder}/Sankey_{hymn['number']}.jpg"
                        
                        # Check uppercase fallback for hymn number
                        final_check = os.path.join(app.static_folder, filename_target)
                        if not os.path.exists(final_check) and os.path.exists(os.path.join(app.static_folder, f"{hymn_folder}/Sankey_{hymn['number']}.JPG")):
                            filename_target = f"{hymn_folder}/Sankey_{hymn['number']}.JPG"

                img_url = url_for('static', filename=filename_target)
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
