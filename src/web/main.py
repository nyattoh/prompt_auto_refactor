import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = FastAPI()

# staticディレクトリのマウント
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# templatesディレクトリの設定
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # ダミーデータでUIを表示
    return templates.TemplateResponse("index.html", {
        "request": request,
        "prompt": "例）この関数をリファクタしてください",
        "output": "ここに最終出力が表示されます",
        "persona": "ペルソナ例",
        "auto_input": "自動入力例",
        "analysis": "分析・評価例",
        "policy": "修正方針例",
        "progress": "進捗例",
        "history": ["リファクタリング履歴1", "リファクタリング履歴2"],
        "final_prompt": "最終調整済みプロンプト例"
    })
