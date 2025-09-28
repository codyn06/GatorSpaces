from flask import Flask, render_template
from datetime import datetime
import re
from playwright.sync_api import sync_playwright
from flask import Flask, render_template, redirect
from time import localtime
import math

app = Flask(__name__)
# Static library info
staticLibraryData = [
    {
        "id": "marston",
        "name": "Marston Science Library",
        "address": "4000 Central Florida Blvd, Gainesville, FL 32611",
        "hours": "8 AM - 1 AM (M-Th), 8 AM - 10 PM (Fri), 10 AM - 6PM (Sat), 10 AM - 1AM (Sun)",
        "mapUrl": "https://www.google.com/maps/place/Marston+Science+Library/data=!4m2!3m1!1s0x0:0xa84d77bf04354a1e",
    },
    {
        "id": "libwest",
        "name": "Library West",
        "address": "1545 W University Ave, Gainesville, FL 32603",
        "hours": "8 AM - 1 AM (M-Th), 8 AM - 10 PM (Fri), 10 AM - 6PM (Sat), 10 AM - 1AM (Sun)",
        "mapUrl": "https://www.google.com/maps/place/Library+West+Humanities+%26+Social+Sciences",
    },
    {
        "id": "education",
        "name": "Education Library",
        "address": "Norman Hall Addition, 618 SW 12th St, Gainesville, FL 32601",
        "hours": "8 AM - 10 PM (M-Th), 8 AM - 5PM (Fri), Closed (Sat), 2 PM to 10 PM (Sun)",
        "mapUrl": "https://www.google.com/maps/place/Education+Library",
    },
    {
        "id": "health",
        "name": "Health Science Center Library",
        "address": "Communicore Building, SW Archer Rd, Gainesville, FL 32610",
        "hours": "7:30 AM - 11:30 PM (M-Th), 7:30 AM - 7 PM (Fri), 8 AM - 5 PM (Sat), 1 PM - 11:30 PM (Sun)",
        "mapUrl": "https://www.google.com/maps/place/UF+Health+Science+Center+Libraries",
    },
    {
        "id": "smathers",
        "name": "Smathers Library",
        "address": "1508 Union Rd, Gainesville, FL 32611",
        "hours": "8 AM - 7 PM (M-Th), 8 AM - 5 PM (Fri), Closed (Sat), Closed (Sun)",
        "mapUrl": "https://www.google.com/maps/place/Smathers+Library",
    },
    {
        "id": "afa",
        "name": "Architecture & Fine Arts Library",
        "address": "UF Fine Arts Complex 201 Fine Arts A, Gainesville, FL 32611",
        "hours": "8 AM - 10 PM (M-Th), 8 AM - 5PM (Fri), Closed (Sat), 2 PM to 10 PM (Sun)",
        "mapUrl": "https://www.google.com/maps/place/The+Architecture+%26+Fine+Arts+Library",
    },
]
def occupancy():
    URL = "https://www.uflib.ufl.edu/status/"
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(5000)
        rendered_text = page.inner_text("body")
        browser.close()

    # Slice library chunks
    LibraryWest = rendered_text[rendered_text.index("Library West"):rendered_text.index("Marston")]
    Marston = rendered_text[rendered_text.index("Marston"):rendered_text.index("Health")]
    HealthScience = rendered_text[rendered_text.index("Health"):rendered_text.index("Architecture")]
    Architecture = rendered_text[rendered_text.index("Architecture"):rendered_text.index("Education")]
    Education = rendered_text[rendered_text.index("Education"):rendered_text.index("Smathers Library")]
    Smathers = rendered_text[rendered_text.index("Smathers Library"):rendered_text.index("231") + 4]

    # Return name, occupancy text, and matching id
    Libraries = [
        ("Library West", LibraryWest, "libwest"),
        ("Marston Science Library", Marston, "marston"),
        ("Health Science Center Library", HealthScience, "health"),
        ("Architecture & Fine Arts Library", Architecture, "afa"),
        ("Education Library", Education, "education"),
        ("Smathers Library", Smathers, "smathers"),
    ]
    return Libraries

'''
#When button clicked (lib_code)
    #Education: EDU
    #Health Science: HSCL
    #Lib West: LW
    #Marston: MSL

    cd = datetime.now()
    year, month, day, hour, min = cd.year,cd.month,cd.day,cd.hour,int(math.ceil(cd.minute/ 30)) * 30
    if min==60:
        min=0
        hour+=1
    end_hour = hour + 1
    end_min = min + 30
    if end_min == 60:
        end_min = 0

    URL = f"https://libcal.uflib.ufl.edu/r/search/{lib_code}?m=t&gid=0&capacity=0&date={year}-{month}-{day}&date-end={year}-{month}-{day}&start={hour}%3A{min}&end=21{end_hour}%3A{end_min}"
    return URL
'''

def build_libcal_url(lib_code):
    # Education: EDU
    # Health Science: HSCL
    # Lib West: LW
    # Marston: MSL

    cd = datetime.now()
    year, month, day, hour, minute = cd.year, cd.month, cd.day, cd.hour, cd.minute
    min = int(math.ceil(minute / 30)) * 30
    if min == 60:
        min = 0
        hour += 1

    end_hour = hour + 1
    end_min = min + 30
    if end_min == 60:
        end_min = 0

    URL = (
        f"https://libcal.uflib.ufl.edu/r/search/{lib_code}"
        f"?m=t&gid=0&capacity=0"
        f"&date={year}-{month}-{day}&date-end={year}-{month}-{day}"
        f"&start={hour}%3A{min}&end={end_hour}%3A{end_min}"
    )
    return URL

@app.route("/check-rooms/<lib_id>")
def check_rooms(lib_id):
    mapping = {
        "education": "EDU",
        "health": "HSCL",
        "libwest": "LW",
        "marston": "MSL",
    }
    if lib_id in mapping:
        url = build_libcal_url(mapping[lib_id])
        return redirect(url)
    else:
        return f"No room-check available for {lib_id}", 404

def colors_and_names():
    raw_libs = occupancy()
    libraries = []

    for name, text, lib_id in raw_libs:
        occ_match = re.search(r"Occupancy[:\s]+(\d+)", text)
        cap_match = re.search(r"Capacity[:\s]+(\d+)", text)

        if occ_match and cap_match:
            occupancy_num = int(occ_match.group(1))
            capacity = int(cap_match.group(1))
            ratio = occupancy_num / capacity
        else:
            occupancy_num, capacity, ratio = 0, 1, 0

        if ratio >= 0.7:
            color = "red"
        elif ratio >= 0.3:
            color = "yellow"
        elif ratio > 0:
            color = "green"
        else:
            color = "gray"

        # ✅ merge static info by id OR name
        static_info = next(
            (s for s in staticLibraryData if s["id"] == lib_id or s["name"] == name),
            {}
        )

        libraries.append({
            "id": lib_id,
            "name": name,
            "occupancy": occupancy_num,
            "capacity": capacity,
            "ratio": ratio,
            "color": color,
            "address": static_info.get("address", "N/A"),
            "hours": static_info.get("hours", "N/A"),
            "mapUrl": static_info.get("mapUrl", "#"),
        })

    return sorted(libraries, key=lambda x: x["ratio"], reverse=True)

@app.route("/")
def home():
    libraries = colors_and_names()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("index.html", libraries=libraries, timestamp=timestamp)


if __name__ == "__main__":
    app.run(debug=True)