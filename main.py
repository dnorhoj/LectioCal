import re
from datetime import datetime, timedelta
from os import environ as environ
import logging

import caldav
import icalendar
import lectio
from tqdm import tqdm

log = logging.getLogger("LectioCalDAV")

def generate_ical(start, end, summary, desc, color, uid):
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
    event_data.add('description', desc)
    event_data.add('color', color)

    event.add_component(event_data)
    

    return event.to_ical()

def main(*, use_tqdm=False):
    # Create lectio obj
    lec = lectio.Lectio(environ.get("LECTIO_INST_ID"))

    # Creds from env vars
    lec.authenticate(
        environ.get('LECTIO_USERNAME'),
        environ.get('LECTIO_PASSWORD')
    )

    # Get calendar from CalDAV URL, username and password
    cal = caldav.DAVClient(
        url=environ.get('CALDAV_URL'),
        username=environ.get('CALDAV_USERNAME'),
        password=environ.get('CALDAV_PASSWORD')
    ).calendar(url=environ.get('CALDAV_URL'))

    # Get start and end dates, without hour, minute, seconds
    start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end = start+timedelta(days=30)

    # Get schedule for student
    sched = lec.get_schedule_for_student(
        lec.get_user_id(),
        start,
        end
    )

    # List of uids, used later for deleting non-existent modules
    uids = []

    # Iterate over all modules
    sched_iter = sched
    if use_tqdm:
        sched_iter = tqdm(sched_iter, "Importing modules into CalDAV")
    else:
        print("Importing modules into CalDAV")
    
    for module in sched_iter:
        # Example: no title: 3.b Da; with title: 3.b Da - Never gonna give you up
        title = module.subject
        if module.title is not None:
            title += f' - {module.title}'
        
        # Get uid from module title get params, and append it to uids list
        uids.append(re.search(r"absid=(.*?)&", module.url)[1])
        
        # Add module url to event description, and optionally add extra info if present
        desc = re.match(r"(.*?)&", module.url)[1]
        if module.extra_info:
            desc += "\n\n" + module.extra_info
        
        # Color info (changed, deleted)
        color = None
        if module.status == 1: # Module changed
            color = "green"
        elif module.status == 2: # Module deleted
            color = "red"

        # Save the event
        cal.save_event(
            ical=generate_ical(
                start=module.start_time,
                end=module.end_time,
                summary=title,
                desc=desc,
                color=color,
                uid=uids[-1]
            ),
        )

    # Get all cal events within start, end
    events = cal.date_search(start, end)

    # Remove leftover events
    print("Checking if there are any untracked modules")
    for e in events:
        # Extract uid from ical
        uid = e.icalendar_instance.subcomponents[0].get("uid")

        if uid not in uids:
            # Get more info for logging
            component = e.icalendar_instance.subcomponents[0]

            start = component.get("dtstart")
            end = component.get("dtend")
            summary = component.get("summary")

            log.warning(f"Deleting module {uid}, start time: {start}, end time: {end}, summary: {summary}")
            e.delete()

if __name__ == '__main__':
    print("Starting Lectio.py ft. CalDAV")
    main(use_tqdm=True)
