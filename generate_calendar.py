import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

URL = "https://www.seahawkssports.com/page4778"

def parse_date_time(date_str, time_str):
    try:
        dt = datetime.strptime(date_str + " " + time_str, "%m/%d/%Y %I:%M %p")
        return dt
    except:
        return None

def create_ics(events):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//JV Softball Auto//EN"
    ]

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

def scrape():
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    events = []

    rows = soup.find_all("tr")

    for row in rows:
        text = row.get_text(" ", strip=True)

        if "JV Softball" not in text:
            continue

        try:
            parts = text.split()

            date = parts[0]
            time = parts[1] + " " + parts[2]

            dt = parse_date_time(date, time)
            if not dt:
                continue

            title = text
            location = "TBD"

            events.append({
                "start": dt,
                "title": title,
                "location": location
            })

        except:
            continue

    return events

events = scrape()
ics = create_ics(events)

with open("calendar.ics", "w") as f:
    f.write(ics)
    
push to main
