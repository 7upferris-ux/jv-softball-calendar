import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

URL = "https://www.seahawkssports.com/page4778"

def parse_datetime(date_str, time_str):
    try:
        return datetime.strptime(date_str + " " + time_str, "%m/%d/%Y %I:%M %p")
    except:
        return None

def scrape_jv_softball():
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")
    events = []

    # Go through all table rows
    for row in soup.find_all("tr"):
        cols = [c.get_text(strip=True) for c in row.find_all("td")]

        if len(cols) < 3:
            continue

        # Only include JV Softball games
        if not any("JV Softball" in c for c in cols):
            continue

        date = cols[0]
        time = cols[1]

        dt = parse_datetime(date, time)
        if not dt:
            continue

        opponent = " vs ".join(cols[2:])  # Combine remaining columns
        title = f"JV Softball {opponent}"

        events.append({
            "start": dt,
            "title": title,
            "location": "TBD"
        })
    return events

def create_ics(events):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//JV Softball Auto//EN"]
    for i, e in enumerate(events):
        start = e["start"]
        end = start + timedelta(hours=2)
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{i}@jvsoftball",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{start.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{end.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{e['title']}",
            f"LOCATION:{e['location']}",
            "END:VEVENT"
        ])
    lines.append("END:VCALENDAR")
    return "\n".join(lines)

# Scrape and create ICS
events = scrape_jv_softball()
ics_content = create_ics(events)

with open("calendar.ics", "w") as f:
    f.write(ics_content)
