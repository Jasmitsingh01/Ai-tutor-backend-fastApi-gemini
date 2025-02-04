from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
import uvicorn
# Import routes here to avoid circular imports
from routes import user_routes, AITutor_routes


# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Project")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://skc-jasmit-singh-ai-tutor-assistant-frontend-ilurrmp5n.vercel.app"],  # Allows all origins
    allow_credentials=True,  # Consider if you need this (cookies, auth headers)
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include Routers
app.include_router(user_routes.router, prefix="/api/users")
app.include_router(AITutor_routes.router, prefix="/api/tutor")


@app.get("/")
def root():
    return "FastAPI Project Running!"


if __name__ == "__main__":  # Important for multiprocessing
    uvicorn.run(app=app, host="0.0.0.0", port=5000, reload=True) #reloa