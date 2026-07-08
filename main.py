from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# Wide-open CORS so the grader browser environment is happy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replace this with your CURRENT simple cloudflared tunnel URL
# (Start it simply with: cloudflared tunnel --url http://localhost:11434)
LOCAL_OLLAMA_TUNNEL = "https://symphony-careers-faster-concentration.trycloudflare.com"

@app.post("/v1/chat/completions")
async def proxy_chat(request: Request):
    body = await request.json()
    
    # Forward the cleaned payload to your local Ollama instance via the tunnel
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{LOCAL_OLLAMA_TUNNEL}/v1/chat/completions",
            json=body
        )
        return response.json()
