from apscheduler.schedulers.blocking import BlockingScheduler
from main import main_difference, main_former, main_latter, main_difference_later
from create_tweet import tweet

scheduler = BlockingScheduler()
# 9-21時→0-12時
scheduler.add_job(main_former, 'cron', hour="14,6", minute="50")
scheduler.add_job(main_latter, 'cron', hour="1,7", minute="0")
scheduler.add_job(main_difference, 'interval', minutes=30)
scheduler.add_job(main_difference_later, 'interval', minutes=30)

# scheduler.add_job(main_latter, 'cron', minute=30)
# scheduler.add_job(test, 'cron', hour=10)

scheduler.start()