from apscheduler.schedulers.blocking import BlockingScheduler
from main import main_difference_former, main_former, main_latter, main_difference_latter
from create_tweet import tweet

scheduler = BlockingScheduler(timezone="Asia/Tokyo")

# 定期
scheduler.add_job(main_former, 'cron', hour="9,17", minute="0")
scheduler.add_job(main_latter, 'cron', hour="10,18", minute="0")

# 更新
# 下2段は教務webメンテンナンス中
scheduler.add_job(main_difference_former, 'cron', hour="0, 1, 4", minute="20", day_of_week="mon, wed, thu, sat, sun")
scheduler.add_job(main_difference_former, 'cron', hour="7-23", minute="20", day_of_week="mon, wed, thu, sat, sun")
scheduler.add_job(main_difference_former, 'cron', hour="0, 1", minute="20", day_of_week="tue, fri")
scheduler.add_job(main_difference_former, 'cron', hour="9-23", minute="20", day_of_week="tue, fri")

scheduler.add_job(main_difference_latter, 'cron', hour="0, 1, 4", minute="45", day_of_week="mon, wed, thu, sat, sun")
scheduler.add_job(main_difference_latter, 'cron', hour="7-23", minute="45", day_of_week="mon, wed, thu, sat, sun")
scheduler.add_job(main_difference_latter, 'cron', hour="0, 1", minute="45", day_of_week="tue, fri")
scheduler.add_job(main_difference_latter, 'cron', hour="9-23", minute="45", day_of_week="tue, fri")

# scheduler.add_job(main_latter, 'cron', minute=30)
# scheduler.add_job(test, 'cron', hour=10)

scheduler.start()