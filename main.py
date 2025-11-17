import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

app = FastAPI(title="School Website API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SchoolInfo(BaseModel):
    name: str = Field(default="École", description="School name")
    address: str
    phone: str
    hours_label: str = Field(description="Human readable hours like 'Ouvert · Ferme à 18h'")
    city: Optional[str] = None
    country: Optional[str] = None
    maps_url: Optional[str] = None


class ContactRequest(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    message: str


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/api/info", response_model=SchoolInfo)
def get_school_info():
    """Public info for the school used by the frontend."""
    address = "58 Bd Ibnou Sina, Casablanca 20210"
    phone = "05229-44803"
    hours = "Ouvert · Ferme à 18h"
    maps_q = address.replace(" ", "+")
    maps_url = f"https://www.google.com/maps/search/?api=1&query={maps_q}"

    return SchoolInfo(
        name="École Ibnou Sina",
        address=address,
        phone=phone,
        hours_label=hours,
        city="Casablanca",
        country="Maroc",
        maps_url=maps_url,
    )


@app.post("/api/contact")
def submit_contact(payload: ContactRequest):
    """
    Receive contact messages from the website. In this basic version, we simply
    acknowledge receipt. This is where you'd normally send an email or store in DB.
    """
    if len(payload.message.strip()) < 5:
        raise HTTPException(status_code=400, detail="Le message est trop court.")

    # In a real app: send email or save to DB. Here we just echo success.
    return {
        "status": "ok",
        "received": {
            "name": payload.name,
            "email": payload.email,
            "phone": payload.phone,
        },
        "message": "Merci pour votre message. Nous vous contacterons bientôt.",
    }


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
