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
        page.wait_for_timeout(500)  # wait for JS
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
    Libraries, _ = occupancy()
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

    # Static library info
    staticLibraryData = [
        {"id":"marston","name":"Marston Science Library","address":"4000 Central Florida Blvd, Gainesville, FL 32611",
         "hours":"8 AM - 1 AM (M-Th), 8 AM - 10 PM (Fri), 10 AM - 6PM (Sat), 10 AM - 1AM (Sun)",
         "mapUrl":"https://www.google.com/maps/place/Marston+Science+Library/data=!4m2!3m1!1s0x0:0xa84d77bf04354a1e?sa=X&ved=1t:2428&ictx=111"},
        {"id":"libwest","name":"Library West","address":"1545 W University Ave, Gainesville, FL 32603",
         "hours":"8 AM - 1 AM (M-Th), 8 AM - 10 PM (Fri), 10 AM - 6PM (Sat), 10 AM - 1AM (Sun)",
         "mapUrl":"https://www.google.com/maps/place/Library+West+Humanities+%26+Social+Sciences/@29.6512978,-82.3428834,17z"},
        {"id":"education","name":"Education Library","address":"Norman Hall Addition, 618 SW 12th St, Gainesville, FL 32601",
         "hours":"8 AM - 10 PM (M-Th), 8 AM - 5PM (Fri), Closed (Sat), 2 PM to 10 PM (Sun)",
         "mapUrl":"https://www.google.com/maps/place/Education+Library/@29.6466447,-82.337686,17z"},
        {"id":"health","name":"Health Science Center Library","address":"Communicore Building, SW Archer Rd, Gainesville, FL 32610",
         "hours":"7:30 AM - 11:30 PM (M-Th), 7:30 AM - 7 PM (Fri), 8 AM - 5 PM (Sat), 1 PM - 11:30 PM (Sun)",
         "mapUrl":"https://www.google.com/maps/place/UF+Health+Science+Center+Libraries/data=!4m2!3m1!1s0x0:0x2a675be5ffd3ccb7"},
        {"id":"smathers","name":"Smathers Library","address":"1508 Union Rd, Gainesville, FL 32611",
         "hours":"8 AM - 7 PM (M-Th), 8 AM - 5 PM (Fri), Closed (Sat), Closed (Sun)",
         "mapUrl":"https://www.google.com/maps/place/Smathers+Library/@29.650953,-82.3440677,17z"},
        {"id":"afa","name":"Architecture & Fine Arts Library","address":"UF Fine Arts Complex 201 Fine Arts A, Gainesville, FL 32611",
         "hours":"8 AM - 10 PM (M-Th), 8 AM - 5PM (Fri), Closed (Sat), 2 PM to 10 PM (Sun)",
         "mapUrl":"https://www.google.com/maps/place/The+Architecture+%26+Fine+Arts+Library/data=!4m2!3m1!1s0x0:0xbcea4923e8ae2093?sa=X&ved=1t:2428&ictx=111"}
    ]

    # Merge data for template
    merged_data = []
    for name, color, occ in zip(names, colors, occupancy_display):
        lib_info = next((lib for lib in staticLibraryData if name.lower() in lib['name'].lower()), {})
        merged_data.append({
            "name": lib_info.get("name", name),
            "address": lib_info.get("address", ""),
            "hours": lib_info.get("hours", ""),
            "mapUrl": lib_info.get("mapUrl", "#"),
            "color": color,
            "occupancy": occ
        })

    # HTML template
    html = """
    <html>
    <head>
        <title>UF Library Occupancy</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            h1 { text-align: center; }
            p { text-align: center; color: #555; }
            .library-list { max-width: 700px; margin: auto; padding: 0; list-style: none; }
            .library-item { display: flex; justify-content: space-between; align-items: center;
                            background: white; margin: 10px 0; padding: 15px; border-radius: 8px;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.1); flex-wrap: wrap; }
            .library-info { display: flex; align-items: center; margin-bottom: 5px; }
            .color-box { width: 20px; height: 20px; border-radius: 50%; margin-right: 15px; }
            .details { font-size: 0.9em; color: #555; margin-left: 35px; }
            .occupancy { font-weight: bold; color: #333; }
            a { text-decoration: none; color: #1a73e8; }
        </style>
    </head>
    <body>
        <h1>UF Library Occupancy</h1>
        <p>Last refreshed: {{ refresh_time }}</p>
        <ul class="library-list">
        {% for lib in data %}
            <li class="library-item">
                <div>
                    <div class="library-info">
                        <div class="color-box" style="background-color: {{ lib.color }};"></div>
                        <span>{{ lib.name }}</span>
                        <span class="occupancy"> ({{ lib.occupancy }})</span>
                    </div>
                    <div class="details">
                        <div>{{ lib.address }}</div>
                        <div>{{ lib.hours }}</div>
                        <div><a href="{{ lib.mapUrl }}" target="_blank">View on Map</a></div>
                    </div>
                </div>
            </li>
        {% endfor %}
        </ul>
    </body>
    </html>
    """

    return render_template_string(html, data=merged_data, refresh_time=refresh_time)

if __name__ == "__main__":
    app.run(debug=True)