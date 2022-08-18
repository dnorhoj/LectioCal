from main import main as sync_cal
from apscheduler.schedulers.blocking import BlockingScheduler

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    print("Running once before starting schedule.")
    sync_cal()
    print("\nStarting scheduler...")
    scheduler.add_job(sync_cal, 'interval', hours=1)
    scheduler.start()