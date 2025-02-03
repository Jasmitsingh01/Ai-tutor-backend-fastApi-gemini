from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base

# Import routes here to avoid circular imports
from routes import user_routes, AITutor_routes


# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Project")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allows all origins
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


if __name__=="main":
    import uvicorn
    uvicorn.run(app=app,host="127.0.0.1",port=5000)