# 📦 Standard library

# 🌐 Third-party
from fastapi import FastAPI

# 📁 Local imports
from app.api.routers import loans
from app.db import models
from app.db.database import (engine)

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(loans.router)