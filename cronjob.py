from apscheduler.schedulers.blocking import BlockingScheduler
from main import main, main_difference

scheduler = BlockingScheduler(timezone="Asia/Tokyo")

# 定期
scheduler.add_job(main, 'cron', hour="9, 17", minute="0")

# 更新
# 下2段は教務webメンテンナンス中
scheduler.add_job(main_difference, 'cron', hour="0, 1, 4", minute="30", day_of_week="mon, wed, thu, sat, sun")
scheduler.add_job(main_difference, 'cron', hour="7-23", minute="30", day_of_week="mon, wed, thu, sat, sun")
scheduler.add_job(main_difference, 'cron', hour="0, 1", minute="30", day_of_week="tue, fri")
scheduler.add_job(main_difference, 'cron', hour="9-23", minute="30", day_of_week="tue, fri")

scheduler.start()