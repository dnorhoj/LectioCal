import json
import re
from datetime import datetime, timedelta
import logging
import os.path

import lectio
import icalendar
import caldav as caldav
import cooltables

class LectioCalDavSynchronizer:
    def __init__(self, lec_inst_id, lec_username, lec_password, cal_url, cal_username, cal_password) -> None:
        """Constructor for LectioCalDavSynchronizer

        Args:
            lec_inst_id (int|str): Lectio institution id
            lec_username (str): Lectio username
            lec_password (str): Lectio password
            cal_url (str): CalDav calendar URL
            cal_username (str): CalDav username
            cal_password (str): CalDav password
        """

        self.log = logging.getLogger("synchronizer")
        logging.basicConfig(level=logging.INFO, format='%(message)s')

        self.lec_inst_id = lec_inst_id
        self.lec_username = lec_username
        self.lec_password = lec_password
        self.cal_url = cal_url
        self.cal_username = cal_username
        self.cal_password = cal_password

        self.lec = self._lec_auth()
        self.lec_user_id = self.lec.get_user_id()
        self.cal = caldav.CalDavClient(
            self.cal_username,
            self.cal_password,
            self.cal_url
        )

        self.team_translations = self._get_team_translations()

    def _lec_auth(self) -> lectio.Lectio:
        """Authenticate lectio module, and return it

        Returns:
            lectio.Lectio: Authenticated Lectio instance
        """
        # Create lectio obj
        lec = lectio.Lectio(self.lec_inst_id)

        # Creds from env vars
        lec.authenticate(
            self.lec_username,
            self.lec_password
        )

        return lec

    def _get_team_translations(self):
        try:
            TEAM_TRANSLATIONS_PATH = os.path.join(os.path.dirname(__file__), '..', 'team_translations.json')

            with open(TEAM_TRANSLATIONS_PATH, 'r') as f:
                return json.load(f)

        except FileNotFoundError:
            self.log.warn("No team translation config found.")
        except json.JSONDecodeError:
            self.log.error(f"Invalid json in {TEAM_TRANSLATIONS_PATH}")
        except:
            self.log.error("Unknown error occured while trying to read team translations")

        return {}

    @staticmethod
    def _get_module_id(module: lectio.Module) -> str:
        """Get lectio module id as caldav id

        Args:
            module (lectio.Module): module

        Returns:
            str: id from module url with lecmod prepended
        """

        return "lecmod"+re.search(r"absid=(.*?)&", module.url)[1]

    def _get_module_title(self, module: lectio.Module) -> str:
        """Get module title

        Args:
            module (lectio.Module): Lectio module

        Returns:
            str: module title
        """

        title = module.subject

        for trans in self.team_translations.keys():
            if trans.lower() in module.subject.lower():
                title = self.team_translations.get(trans)

        if module.title is not None:
            title += f' - {module.title}'
        if module.extra_info:
            title += ' [+]'

        return title

    @staticmethod
    def _get_module_desc(module: lectio.Module) -> str:
        """Get module description

        Args:
            module (lectio.Module): Lectio module

        Returns:
            str: Module description, with url
        """

        desc = re.match(r"(.*?)&", module.url)[1]
        if module.room:
            desc = module.room+"\n"+desc
        if module.extra_info:
            desc += "\n\n" + module.extra_info

        return desc.replace("\r\n", "\n")

    @staticmethod
    def _get_module_color(module: lectio.Module) -> str:
        """Get module color as string

        Args:
            module (lectio.Module): Lectio module

        Returns:
            str: color as string (either None, "green" or "red")
        """

        color = None
        if module.status == 1: # Module changed
            color = "green"
        elif module.status == 2: # Module deleted
            color = "red"

        return color

    def add_or_update_module(self, module: lectio.Module) -> None:
        """Adds module to CalDav

        Args:
            module (lectio.Module): Lectio module
        """

        self.cal.add_event(
            uid=self._get_module_id(module),
            summary=self._get_module_title(module),
            desc=self._get_module_desc(module),
            color=self._get_module_color(module),
            start=module.start_time,
            end=module.end_time,
        )


    def event_module_equal(self, event: icalendar.Calendar, module: lectio.Module) -> bool:
        """Compare if module and calendar is equal

        Args:
            event (icalendar.Calendar): iCal instance
            module (lectio.Module): Module instance

        Returns:
            bool: Whether event and module are equal
        """
        component = event.subcomponents[0]

        try:
            return (component.get("uid") == self._get_module_id(module) and
                    component.get("summary") == self._get_module_title(module) and
                    component.get("description") == self._get_module_desc(module) and
                    component.get("dtstart").dt.replace(tzinfo=None) == module.start_time and
                    component.get("dtend").dt.replace(tzinfo=None) == module.end_time and
                    component.get("color") == self._get_module_color(module))
        except AttributeError:
            return False

    def sync(self, start:datetime=None):
        """Starts synchronization 30 days forward

        Args:
            start (datetime, optional): Start date. Defaults to now.
        """

        # Get start and end dates, without hour, minute, seconds
        if start is None:
            start = datetime.now()

        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start+timedelta(days=31)

        # Get schedule for student
        sched = self.lec.get_schedule_for_student(
            self.lec_user_id,
            start,
            end,
            False
        )
        self.log.debug(f"Got {len(sched)} modules from lectio")

        sched_lookup = [self._get_module_id(module) for module in sched]

        # Get events to see which should be updated/removed/inserted
        events = self.cal.get_events(start, end)
        self.log.debug(f"Got {len(events)} events from CalDav")

        # For printing afterwards
        added = 0
        removed = 0
        updated = 0
        
        self.log.info("Updating/removing existing events...")
        # Remove or update modules
        for event in events:
            uid = event.subcomponents[0].get("uid")

            try:
                i = sched_lookup.index(uid) # Will raise exception if not found

                # Module exists
                module = sched[i]

                # Remove module from schedule
                sched_lookup.pop(i)
                sched.pop(i)

                # Only update if changed
                if not self.event_module_equal(event, module):
                    updated += 1
                    self.add_or_update_module(module)

            except ValueError:
                # Module does not exist in lectio's schedule
                # Therefore we delete it from caldav
                removed += 1
                self.cal.delete_event(uid)

        self.log.info("Adding new modules to calendar...")
        # Add remaining modules (new modules)
        for module in sched:
            added += 1
            self.add_or_update_module(module)

        print(cooltables.create_table([
            ["Overview", ""],

            ["Updated", str(updated)],
            ["Added", str(added)],
            ["Removed", str(removed)],
        ], theme=cooltables.CLEAN_THEME))

if __name__ == '__main__':
    from os import environ

    # Run on main

    print("Starting Lectio.py ft. CalDAV")
    sync = LectioCalDavSynchronizer(
        lec_inst_id=environ["LECTIO_INST_ID"],
        lec_username=environ["LECTIO_USERNAME"],
        lec_password=environ["LECTIO_PASSWORD"],
        cal_url=environ["CALDAV_URL"],
        cal_username=environ["CALDAV_USERNAME"],
        cal_password=environ["CALDAV_PASSWORD"],
    )

    sync.sync()
