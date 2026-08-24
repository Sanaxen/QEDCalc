QEDCalc 全テスト一括実行バッチ
================================

使い方
------
1. run_all_tests_with_log.bat を QEDCalc のルートフォルダへコピーします。
   run_tests.bat / setup_env.bat / requirements.txt があるフォルダです。

2. run_all_tests_with_log.bat をダブルクリックして実行します。

3. .venv が無ければ setup_env.bat が自動実行されます。

4. 全 pytest が終了すると、QEDCalc フォルダ内に

   test_results\full_test_YYYYMMDD_HHMMSS.zip

   が生成されます。

5. その ZIP ファイルを ChatGPT に添付してください。

ZIP に含まれるもの
------------------
- pytest_full.log : pytest -vv の全出力と遅いテスト上位100件
- environment.txt : Python / SymPy / pytest / pip freeze / OS情報
- summary.txt     : pytest終了コードとログ名

補足
----
- テスト途中でも pytest_full.log へ逐次書き込まれます。
- pytest が失敗してもログは消えません。
- exit_code=0 は全テスト成功です。
- exit_code=1 は通常のテスト失敗です。
- その他の終了コードでも、ログをそのまま送ってください。
