"""One-screen demo server. Run: cd marketear && python ui/server.py  (default port 8000). Uses fp32 model on CPU; first request loads the model."""
import sys, os, json, glob, threading
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "src"))
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import uvicorn
app = FastAPI(); ME = None; LOCK = threading.Lock()
SAMPLES = os.path.join(HERE, "..", "ui", "samples")
def get():
    global ME
    if ME is None:
        import marketear; ME = marketear.MarketEar()
    return ME
@app.get("/", response_class=HTMLResponse)
def index(): return open(os.path.join(HERE, "index.html")).read()
@app.get("/samples")
def samples(): return json.load(open(os.path.join(SAMPLES, "samples.json")))
@app.get("/sample/{name}")
def sample(name): return FileResponse(os.path.join(SAMPLES, os.path.basename(name)))
@app.post("/listen")
async def listen(audio: UploadFile = File(...), cnr: str = Form("none")):
    import marketear
    tmp = "/tmp/_me_upload" + os.path.splitext(audio.filename or "x.webm")[1]
    open(tmp, "wb").write(await audio.read())
    try:
        with LOCK:
            a = marketear.load_audio(tmp)
            try: r = get().listen(a, None if cnr == "none" else float(cnr))
            except Exception as e: return JSONResponse({"decision": "error", "reason": str(e)}, status_code=500)
    finally:   # privacy: the uploaded audio and its converted copy are deleted as soon as the request ends
        for p in (tmp, "/tmp/_me_in.wav"):
            if os.path.exists(p): os.remove(p)
    return r
if __name__ == "__main__": uvicorn.run(app, host=os.environ.get("HOST", "127.0.0.1"), port=int(sys.argv[1]) if len(sys.argv) > 1 else 8000)
