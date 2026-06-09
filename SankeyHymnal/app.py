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
            # 🖼️ PRODUCTION-READY MULTI-FOLDER ROUTING ENGINE
            # -------------------------------------------------------------
            image_urls = []
            
            for p in pages:
                try:
                    page_num_int = int(p)
                except ValueError:
                    page_num_int = 0

                # Strategy 1: Attempt to route using Calculated Page Number
                if page_num_int > 0:
                    folder_target = "pages" if page_num_int <= 1000 else "pages2"
                    filename_target = f"{folder_target}/{page_num_int}.png"
                    
                    # Verify using relative deployment directory path mapping
                    full_check_path = os.path.join(app.static_folder, filename_target)
                    
                    # Case-Insensitive Extension Check (.png vs .PNG)
                    if not os.path.exists(full_check_path):
                        alt_check_path = os.path.join(app.static_folder, f"{folder_target}/{page_num_int}.PNG")
                        if os.path.exists(alt_check_path):
                            filename_target = f"{folder_target}/{page_num_int}.PNG"
                        else:
                            # Strategy 2: If page file doesn't exist, fall back to Hymn Number routing
                            try:
                                hymn_num_int = int(hymn["number"])
                            except ValueError:
                                hymn_num_int = 0
                            
                            hymn_folder = "pages" if hymn_num_int <= 1000 else "pages2"
                            filename_target = f"{hymn_folder}/{hymn['number']}.png"
                            
                            # Final double-check for uppercase .PNG on the hymn number fallback
                            final_check = os.path.join(app.static_folder, filename_target)
                            if not os.path.exists(final_check) and os.path.exists(os.path.join(app.static_folder, f"{hymn_folder}/{hymn['number']}.PNG")):
                                filename_target = f"{hymn_folder}/{hymn['number']}.PNG"
                else:
                    # Strategy 3: Complete safety baseline if data parsing fails entirely
                    filename_target = f"pages/{hymn['number']}.png"

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
