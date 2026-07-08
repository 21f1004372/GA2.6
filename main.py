from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("proxy")

app = FastAPI()

# Wide open CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paste your active cloudflared tunnel base URL here (NO trailing slash)
# e.g., "https://your-subdomain.trycloudflare.com"
LOCAL_OLLAMA_TUNNEL = "https://symphony-careers-faster-concentration.trycloudflare.com"

@app.options("/{path:path}")
async def preflight_handler():
    """Explicitly intercept and green-light browser preflight checks."""
    return Response(status_code=200)

@app.api_route("/v1/chat/completions", methods=["POST", "OPTIONS"])
async def proxy_chat(request: Request):
    if request.method == "OPTIONS":
        return Response(status_code=200)
        
    try:
        body = await request.json()
        logger.info(f"Forwarding payload to Ollama: {body}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{LOCAL_OLLAMA_TUNNEL.rstrip('/')}/v1/chat/completions",
                json=body,
                headers={"Host": "localhost:11434"}  # Mimic local host header
            )
            
            logger.info(f"Ollama responded with status: {response.status_code}")
            return Response(
                content=response.content, 
                status_code=response.status_code, 
                media_type="application/json"
            )
            
    except Exception as e:
        logger.error(f"Proxy generation failed: {str(e)}")
        # Fallback response ensuring CORS stays alive even on internal error
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")
