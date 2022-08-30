from datetime import datetime
from typing import List
import icalendar
from bs4 import BeautifulSoup
import requests

# Don't wanna craft the xml lol
SEARCH_STRING = '''<?xml version='1.0' encoding='utf-8'?>
<C:calendar-query xmlns:D="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav"><D:prop><C:calendar-data><C:expand start="{0}" end="{1}"/></C:calendar-data></D:prop><C:filter><C:comp-filter name="VCALENDAR"><C:comp-filter name="VEVENT"><C:time-range start="{0}" end="{1}"/></C:comp-filter></C:comp-filter></C:filter></C:calendar-query>'''


class CalDavClient():
    def __init__(self, username: str, password: str, cal_url: str) -> None:
        self.cal_url = cal_url

        self.session = requests.Session()
        self.session.auth = (username, password)

    def _request(self, method, url, **kwargs):
        r = self.session.request(method, url, **kwargs)

        if (not r.ok):
            print(r.status_code)
            print(r.text)
            raise Exception(
                f"Problem encountered on url: \"{url}\", method: \"{method}\"")

        return r

    @staticmethod
    def _generate_ical(start: datetime, end: datetime, summary: str, location: str, desc: str, uid: str, color: str = None) -> str:
        # Create calendar instance
        event = icalendar.Calendar()
        event.add('prodid', '-//dnorhoj//lectio.py//da_DK')
        event.add('version', '2.0')

        event_data = icalendar.Event()

        # Add event_data fields
        event_data.add('dtstamp', datetime.now())
        event_data.add('uid', uid)
        event_data.add('dtstart', start)
        event_data.add('dtend', end)
        event_data.add('summary', summary)
        event_data.add('location', location)
        event_data.add('description', desc)
        if color is not None:
            event_data.add('color', color)

        event.add_component(event_data)

        return event.to_ical()

    def add_event(self, start, end, summary, location, desc, uid, color=None):
        self._request(
            "PUT",
            f"{self.cal_url}/{uid}.ics",
            data=self._generate_ical(
                start, end, summary, location, desc, uid, color)
        )

    def delete_event(self, uid: str) -> None:
        self._request("DELETE", f"{self.cal_url}/{uid}.ics")

    def get_events(self, start: datetime, end: datetime) -> List[icalendar.Calendar]:
        start = start.strftime("%Y%m%dT%H%M%SZ")
        end = end.strftime("%Y%m%dT%H%M%SZ")

        r = self._request(
            "REPORT",
            self.cal_url,
            data=SEARCH_STRING.format(start, end),
            headers={"Content-Type": "application/xml"}
        )

        soup = BeautifulSoup(r.text, 'xml')

        events = []

        for cal in soup.find_all("C:calendar-data"):
            events.append(icalendar.Calendar.from_ical(cal.text))

        return events
