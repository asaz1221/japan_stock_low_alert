@echo off
REM ===========================================
REM 日本株テスト通知 一発実行（UTF-8 .env 自動作成）
REM ===========================================

REM 1. dataフォルダを作成（なければ）
if not exist "data" mkdir data

REM 2. CSVを作成（symbol列が必ず認識される）
> data\tickers.csv (
    echo symbol,name
    echo 7203.T,トヨタ自動車
    echo 6758.T,ソニー
)

REM 3. .env を UTF-8 で作成（既存があれば上書き）
(
    echo IFTTT_WEBHOOK_URL=https://maker.ifttt.com/trigger/stock_alert/with/key/dFCRRduzGG8v4_PP4FYiaA
) > .env

REM 4. check.py を実行
python check.py

REM 5. 完了メッセージ
echo.
echo ===== 完了 =====
pause
