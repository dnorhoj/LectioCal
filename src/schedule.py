from main import main as sync_cal
from apscheduler.schedulers.blocking import BlockingScheduler

if __name__ == '__main__':
    # Create scheduler
    scheduler = BlockingScheduler()
    print("Running once before starting schedule.")
    sync_cal()

    print("\nStarting scheduler...")
    scheduler.add_job(sync_cal, 'cron', hour="*")

    # Start blocking scheduler, which will run until program is terminated
    scheduler.start()