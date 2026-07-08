from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# Keep wide-open CORS so the grader can talk to Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your active trycloudflare.com URL here
LOCAL_OLLAMA_TUNNEL = "https://symphony-careers-faster-concentration.trycloudflare.com"

@app.options("/{path:path}")
async def preflight():
    return Response(status_code=200)

@app.post("/v1/chat/completions")
async def proxy_chat(request: Request):
    try:
        body = await request.json()
        
        # Prepare headers to forward
        headers = {}
        for k, v in request.headers.items():
            if k.lower() not in ["host", "origin", "referer", "content-length"]:
                headers[k] = v
                
        # Force a local host header so Ollama accepts it natively
        headers["Host"] = "localhost:11434"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{LOCAL_OLLAMA_TUNNEL.rstrip('/')}/v1/chat/completions",
                json=body,
                headers=headers
            )
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type="application/json"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
