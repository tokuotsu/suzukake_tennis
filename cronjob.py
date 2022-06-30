from apscheduler.schedulers.blocking import BlockingScheduler
from main import main_former, main_latter
from create_tweet import tweet

scheduler = BlockingScheduler()
scheduler.add_job(main_former, 'cron', hour="9-21", minute=0)
# scheduler.add_job(main_latter, 'cron', minute=30)
# scheduler.add_job(test, 'cron', hour=10)

scheduler.start()