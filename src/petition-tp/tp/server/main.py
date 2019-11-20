from fastapi import FastAPI
from .security import router as security_router
from .petition import router as petition_router

app = FastAPI(
    title="Sawtooth Petition API",
    description="Restful API for the Petition of the DDDC pilot project over sawtooth",
    version="0.0.1",
    redoc_url=None,
)

app.include_router(security_router)
app.include_router(petition_router)
