from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from app.api.endpoints import knowledge_base, chatbot, post_call
from app.core.config import settings
import os
from fastapi.routing import APIRoute
from fastapi.routing import Mount

app = FastAPI(
    title="Barbeque Nation Chatbot API",
    description="API for handling Barbeque Nation restaurant enquiries and bookings",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Print current working directory for debugging
print(f"Current working directory: {os.getcwd()}")

# Mount static files directory for assets (e.g., CSS, JS, images if any)
# This allows accessing files like http://localhost:8000/static/index.html
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(knowledge_base.router, prefix="/api/knowledge", tags=["Knowledge Base"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["Chatbot"])
app.include_router(post_call.router, prefix="/api/post-call", tags=["Post-Call Analysis"])

# Temporarily serve a plain text response at the root URL "/" to test the route
@app.get("/")
async def read_root():
    return PlainTextResponse("Chatbot server is running!")

# Print registered routes for debugging
print("Registered routes:")
for route in app.routes:
    if isinstance(route, APIRoute):
        print(f"- {route.path} ({route.methods})")
    elif isinstance(route, Mount):
        print(f"- {route.path} (Mounted: {route.name})")
    else:
        print(f"- {route.path} (Unknown route type)")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 