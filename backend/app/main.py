from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, vault

app = FastAPI(title="PasswordVault API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(vault.router)

@app.get("/")
def root():
    return {"message": "PasswordVault API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
