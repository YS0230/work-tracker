@echo off
echo 啟動工作事項記錄系統...

echo 安裝後端依賴...
cd backend
pip install -r requirements.txt

echo 啟動後端服務...
start cmd /k "python run.py"

echo 等待後端啟動...
timeout /t 3

echo 安裝前端依賴...
cd ..\frontend
call npm install

echo 啟動前端服務...
start cmd /k "npm run serve"

echo 系統啟動完成!
echo 前端: http://localhost:8080
echo 後端: http://localhost:5000

pause