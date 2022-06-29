from apscheduler.schedulers.blocking import BlockingScheduler
from main import main, test
from create_tweet import tweet

scheduler = BlockingScheduler()
scheduler.add_job(main, 'cron', minute=0)
scheduler.add_job(main, 'cron', minute=30)
scheduler.add_job(test, 'cron', hour=10)

scheduler.start()