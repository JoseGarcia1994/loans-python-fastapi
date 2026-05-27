# 📦 Standard library

# 🌐 Third-party
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 📁 Local imports
from app.api.routers import loans, users, auth, admin, payments
from app.db import models
from app.db.database import (engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.include_router(loans.router, prefix="/loans")
app.include_router(users.router, prefix="/user")
app.include_router(auth.router, prefix="/auth")
app.include_router(admin.router, prefix="/admin")
app.include_router(payments.router, prefix="/payments")