from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

# Ensure wide-open CORS so the grader can talk to Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paste your active trycloudflare.com URL here
LOCAL_OLLAMA_TUNNEL = "https://ga2-6-jb23.onrender.com" # Update this to your current .trycloudflare.com link if it changed

@app.options("/{path:path}")
async def preflight():
    return Response(status_code=200)

@app.post("/v1/chat/completions")
async def proxy_chat(request: Request):
    try:
        body = await request.json()
        
        # Extract the clean hostname from your tunnel URL (e.g., "subdomain.trycloudflare.com")
        tunnel_host = LOCAL_OLLAMA_TUNNEL.replace("https://", "").replace("http://", "").split("/")[0]
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{LOCAL_OLLAMA_TUNNEL.rstrip('/')}/v1/chat/completions",
                json=body,
                headers={
                    "Host": tunnel_host,  # Match the tunnel's public host instead of localhost
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", # Mask Render's identity
                    "Accept": "application/json"
                }
            )
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type="application/json"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
