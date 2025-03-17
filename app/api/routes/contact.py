# app/api/routes/contact.py
from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter()

@router.post("/contact")
async def proxy_to_google_form(data: dict):
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdsszAEJYAt4d_C-RsAr6Ziv4YALfC3d9GL_KiTsF-dYE3KyA/formResponse"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                form_url,
                data={
                    "entry.2005620554": data.get("name"),
                    "entry.1045781291": data.get("email"),
                    "entry.839337160": data.get("message")
                }
            )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))