from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .routers import salary

app = FastAPI()

# Mount các route logic có prefix /api
app.include_router(salary.router, prefix="/api")

# Mount thư mục static để phục vụ index.html, css, js, ...
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route gốc trả về giao diện
@app.get("/", response_class=HTMLResponse)
def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()
