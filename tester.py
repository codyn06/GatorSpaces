from flask import Flask, render_template_string
from playwright.sync_api import sync_playwright
import re
from datetime import datetime

app = Flask(__name__)

# Scraping function
def occupancy():
    URL = "https://www.uflib.ufl.edu/status/"
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(5000)  # wait for JS
        rendered_text = page.inner_text("body")
        browser.close()

    # Slice library text
    LibraryWest = rendered_text[rendered_text.index("Library West"):rendered_text.index("Marston")]
    Marston = rendered_text[rendered_text.index("Marston"):rendered_text.index("Health")]
    HealthScience = rendered_text[rendered_text.index("Health"):rendered_text.index("Architecture")]
    Architecture = rendered_text[rendered_text.index("Architecture"):rendered_text.index("Education")]
    Education = rendered_text[rendered_text.index("Education"):rendered_text.index("Smathers Library")]
    Smathers = rendered_text[rendered_text.index("Smathers Library"):rendered_text.index("231")+4]

    Libraries = [LibraryWest, Marston, HealthScience, Architecture, Education, Smathers]
    LibraryNames = ["Library West", "Marston", "Health Science", "Architecture", "Education", "Smathers"]
    return Libraries, LibraryNames

# Compute colors safely
def colors_and_names():
    Libraries, LibraryNames = occupancy()
    colors = []

    for lib_text in Libraries:
        occ_match = re.search(r"Occupancy[:\s]+(\d+)", lib_text)
        cap_match = re.search(r"Capacity[:\s]+(\d+)", lib_text)

        if occ_match and cap_match:
            occupancy_num = int(occ_match.group(1))
            capacity = int(cap_match.group(1))
            ratio = occupancy_num / capacity

            if ratio >= 0.7:
                colors.append("red")
            elif ratio >= 0.3:
                colors.append("yellow")
            else:
                colors.append("green")
        else:
            colors.append("gray")  # default if data missing

    return LibraryNames, colors

# Flask route
@app.route("/")
def home():
    names, colors = colors_and_names()
    Libraries, _ = occupancy()  # get raw library text to extract occupancy numbers
    refresh_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extract occupancy / capacity for display
    occupancy_display = []
    for lib_text in Libraries:
        occ_match = re.search(r"Occupancy[:\s]+(\d+)", lib_text)
        cap_match = re.search(r"Capacity[:\s]+(\d+)", lib_text)
        if occ_match and cap_match:
            occupancy_display.append(f"{occ_match.group(1)} / {cap_match.group(1)}")
        else:
            occupancy_display.append("N/A")

    html = """
    <html>
    <head>
        <title>UF Library Occupancy</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            h1 { text-align: center; }
            p { text-align: center; color: #555; }
            .library-list { max-width: 500px; margin: auto; padding: 0; list-style: none; }
            .library-item { display: flex; justify-content: space-between; align-items: center;
                            background: white; margin: 10px 0; padding: 15px; border-radius: 8px;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .color-box { width: 20px; height: 20px; border-radius: 50%; margin-right: 15px; }
            .library-info { display: flex; align-items: center; }
            .occupancy { font-weight: bold; color: #333; }
        </style>
    </head>
    <body>
        <h1>UF Library Occupancy</h1>
        <p>Last refreshed: {{ refresh_time }}</p>
        <ul class="library-list">
        {% for name, color, occ in data %}
            <li class="library-item">
                <div class="library-info">
                    <div class="color-box" style="background-color: {{ color }};"></div>
                    <span>{{ name }}</span>
                </div>
                <div class="occupancy">{{ occ }}</div>
            </li>
        {% endfor %}
        </ul>
    </body>
    </html>
    """

    data = zip(names, colors, occupancy_display)
    return render_template_string(html, data=data, refresh_time=refresh_time)

if __name__ == "__main__":
    app.run(debug=True)