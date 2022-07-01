# Suzukake_tennis
## 概要
テニスコートの空き状況をツイートするボット
## 注意事項
* herokuでの運用を前提にしている。

* 各キーの設定は`config.py`に書く（`config_example.py`参照）か、herokuのConfig Varsで設定する。その場合、MATRIXに関してはリスト型を使えないので以下のように設定する。
  ```bash
  MATRIX="X,X,X,X,X,X,X,X,X,X|X,X,X,X,X,X,X,X,X,X|X,X,X,X,X,X,X,X,X,X|X,X,X,X,X,X,X,X,X,X|X,X,X,X,X,X,X,X,X,X|X,X,X,X,X,X,X,X,X,X|X,X,X,X,X,X,X,X,X,X"
  ```
  
* heroku上のBuildpacksは以下を追加

  * `heroku/python`
  * `https://github.com/heroku/heroku-buildpack-google-chrome.git`
  * `https://github.com/heroku/heroku-buildpack-chromedriver.git`

* heroku関連
  ```bash
  # ログ
  heroku logs --tail
  # bash
  heroku run bash
  # タイムゾーンの設定（必須）
  heroku config:add TZ=Asia/Tokyo
  ```

* 定期実行

  以下のような`python`ファイルを用意

  ```python
  # cronjob.py
  
  from apscheduler.schedulers.blocking import BlockingScheduler
  
  scheduler = BlockingScheduler(timezone="Asia/Tokyo")
  scheduler.add_job(main_former, 'cron', minute="0")
  
  scheduler.start()
  ```
  
  ```bash
  # Procfile
  clock: python cronjob.py
  ```
  
  ```bash
  heroku ps:scale clock=1
  ```
  
  
  
* デバッグ・デプロイ

  デバッグ時は、main.pyの`is_debag=True`で、呟かずにプリントだけできる。

  デプロイ時は、ローカルで`main_difference_former()`と`main_difference_latter()`を実行して`zenkai_former.txt`と`zenkai_latter.txt`を作成してから、必ず`is_debag=False`にしてデプロイする。

  面倒な場合は、最大1時間変更分を呟かないが、`zenkai_former.txt`と`zenkai_latter.txt`なしでデプロイする。

