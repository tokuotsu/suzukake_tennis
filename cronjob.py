from apscheduler.schedulers.blocking import BlockingScheduler
from main import main_difference, main_former, main_latter
from create_tweet import tweet

scheduler = BlockingScheduler()
# 9-21時→0-12
scheduler.add_job(main_former, 'cron', hour="0-14", minute=0)
scheduler.add_job(main_latter, 'cron', hour="0-14", minute=30)
scheduler.add_job(main_difference, 'interval', minute=15)

# scheduler.add_job(main_latter, 'cron', minute=30)
# scheduler.add_job(test, 'cron', hour=10)

scheduler.start()