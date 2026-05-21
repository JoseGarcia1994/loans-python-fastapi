# 📦 Standard library

# 🌐 Third-party
from fastapi import FastAPI

# 📁 Local imports
from app.api.routers import loans, users, auth, admin
from app.db import models
from app.db.database import (engine)

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(loans.router, prefix="/loans")
app.include_router(users.router, prefix="/user")
app.include_router(auth.router, prefix="/auth")
app.include_router(admin.router, prefix="/admin")