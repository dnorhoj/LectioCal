from main import LectioCalDavSynchronizer
from apscheduler.schedulers.blocking import BlockingScheduler
from os import environ

# Create scheduler
scheduler = BlockingScheduler()
synchronizer = LectioCalDavSynchronizer(
    lec_inst_id=environ["LECTIO_INST_ID"],
    lec_username=environ["LECTIO_USERNAME"],
    lec_password=environ["LECTIO_PASSWORD"],
    cal_url=environ["CALDAV_URL"],
    cal_username=environ["CALDAV_USERNAME"],
    cal_password=environ["CALDAV_PASSWORD"],
)

print("Running once before starting schedule.")
synchronizer.sync()

print("\nStarting scheduler...")
scheduler.add_job(synchronizer.sync, 'cron', hour="*")

# Start blocking scheduler, which will run until program is terminated
scheduler.start()