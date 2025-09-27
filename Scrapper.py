from playwright.sync_api import sync_playwright
import re

def occupancy():
    URL = "https://www.uflib.ufl.edu/status/"
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle")  # wait for JS to load
        page.wait_for_timeout(5000)  # extra wait for dynamic content
        # Get all visible text on the page
        rendered_text = page.inner_text("body")

        browser.close()

    # Print the entire rendered text
    #print(rendered_text)
    LibraryWest=rendered_text[rendered_text.index("Library West"):rendered_text.index("Marston")]
    Marston=rendered_text[rendered_text.index("Marston"):rendered_text.index("Health")]
    HealthScience=rendered_text[rendered_text.index("Health"):rendered_text.index("Architecture")]
    Architecture=rendered_text[rendered_text.index ("Architecture"):rendered_text.index("Education")]
    Education=rendered_text[rendered_text.index("Education"):rendered_text.index("Smathers Library")]
    Smathers=rendered_text[rendered_text.index("Smathers Library"):rendered_text.index("231")+4]
    Libraries=[LibraryWest,Marston,HealthScience,Architecture,Education,Smathers]
    return Libraries
def color():
    Libraries=occupancy()
    colors=[]
    for i in Libraries:
        StringoccupanyNum=i[i.index("Occupancy"):i.index("Capacity:")]
        occupancyNum=int(re.search(r'\d+', StringoccupanyNum).group())
        Stringcapcity=i[i.index("Capacity:"):]
        capacity=int(re.search(r'\d+', Stringcapcity).group())
        print(Libraries[4])
        if i!="Smathers":
            if occupancyNum/capacity>=0.7:
                colors.append("red")
                print(i)
            elif occupancyNum/capacity>=0.3:
                colors.append("yellow")
                print(i)
            else:
                colors.append("green")
                print(i)
    return colors