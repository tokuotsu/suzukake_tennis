# Suzukake_tennis
## 概要
テニスコートの空き状況をツイートするボット
## 注意事項
* herokuでの運用を前提にしている。

* 各キーの設定は`config.py`に書く（`config_example.py`参照）か、herokuのConfig Varsで設定する。その場合、MATRIXに関してはリスト型を使えないので以下のように設定する。
  ```bash
  MATRIX=X,X,X,X,X,X,X,X,X,X|X,X,X,X,X,X,X,X,X,X|X,X,X,X,X,X,X,X,X,X|X,X,X,X,X,X,X,X,X,X|X,X,X,X,X,X,X,X,X,X|X,X,X,X,X,X,X,X,X,X|X,X,X,X,X,X,X,X,X,X
  ```
* heroku上のBuildpacksは以下を追加

  * `heroku/python`
  * `https://github.com/heroku/heroku-buildpack-google-chrome.git`
  * `https://github.com/heroku/heroku-buildpack-chromedriver.git`