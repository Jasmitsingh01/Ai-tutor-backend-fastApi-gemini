from fastapi import FastAPI
from database import engine
from models import Base

# Import routes here to avoid circular imports
from routes import user_routes,AITutor_routes


# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Project")


# Include Routers
app.include_router(user_routes.router, prefix="/users")
app.include_router(AITutor_routes.router,prefix="/tutor")

@app.get("/")
def root():
    return "FastAPI Project Running!"