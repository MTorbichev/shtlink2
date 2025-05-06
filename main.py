import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import random
import string
import qrcode
import base64
from io import BytesIO

bd = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

class Link(BaseModel):
    url: str


def genshort():
    return ''.join(random.choices(string.ascii_letters, k=5))


def genqr(link):
    qr_code = qrcode.QRCode(box_size=10, border=4)
    qr_code.add_data(link)
    qr_code.make(fit=True)
    img = qr_code.make_image(fill_color="black", back_color="white").convert("RGBA")
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("site.html", {"request": request})


@app.post("/short")
async def shortlink(req: Link, request: Request):
    shtlll = genshort()
    bd[shtlll] = req.url
    base_url = str(request.base_url).rstrip('/')
    shorturl = f"{base_url}/{shtlll}"
    qrcodes = genqr(shorturl)
    return {"shtlll": shorturl, "qrcodes": f"data:image/png;base64,{qrcodes}"}


@app.get("/{shtlll}")
async def redirect_to_full(shtlll: str):
    if shtlll in bd:
        return RedirectResponse(bd[shtlll])
    return {"error": "Ссылка не найдена"}