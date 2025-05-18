from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
from app.services.knowledge_base import knowledge_base
import os
from app.core.config import settings

router = APIRouter()

@router.post("/upload")
async def upload_knowledge_base(file: UploadFile = File(...)):
    """Upload a new knowledge base document"""
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only .docx files are allowed")
    
    # Create knowledge base directory if it doesn't exist
    os.makedirs(settings.KNOWLEDGE_BASE_DIR, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(settings.KNOWLEDGE_BASE_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Reload knowledge base
    knowledge_base._load_knowledge_base()
    
    return {"message": f"Successfully uploaded {file.filename}"}

@router.get("/restaurants")
async def list_restaurants():
    """List all restaurants in the knowledge base"""
    return {"restaurants": list(knowledge_base.kb_data.keys())}

@router.get("/cities")
async def list_cities():
    """List all cities with restaurants"""
    cities = set()
    for data in knowledge_base.kb_data.values():
        if "location" in data:
            city = data["location"].split(",")[0].strip()
            cities.add(city)
    return {"cities": list(cities)}

@router.get("/search")
async def search_knowledge_base(query: str):
    """Search across all restaurants' information"""
    results = {}
    for restaurant_name, data in knowledge_base.kb_data.items():
        # Search in FAQ
        faq_result = knowledge_base.search_faq(restaurant_name, query)
        if faq_result:
            results[restaurant_name] = {"faq": faq_result}
        
        # Search in menu
        menu = data.get("menu", {})
        menu_results = {
            item: price for item, price in menu.items()
            if query.lower() in item.lower()
        }
        if menu_results:
            if restaurant_name not in results:
                results[restaurant_name] = {}
            results[restaurant_name]["menu"] = menu_results
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No results found for '{query}'")
    
    return {"results": results}

@router.get("/restaurant/{restaurant_name}/info")
async def get_restaurant_info(restaurant_name: str):
    """Get all information about a specific restaurant"""
    info = knowledge_base.get_restaurant_info(restaurant_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"Restaurant {restaurant_name} not found")
    return info

@router.get("/restaurant/{restaurant_name}/timings")
async def get_restaurant_timings(restaurant_name: str):
    """Get operating hours for a specific restaurant"""
    timings = knowledge_base.get_restaurant_timings(restaurant_name)
    if not timings:
        raise HTTPException(status_code=404, detail=f"Timings not found for {restaurant_name}")
    return {"timings": timings}

@router.get("/restaurant/{restaurant_name}/contact")
async def get_restaurant_contact(restaurant_name: str):
    """Get contact information for a specific restaurant"""
    contact = knowledge_base.get_contact_info(restaurant_name)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact information not found for {restaurant_name}")
    return {"contact": contact} 