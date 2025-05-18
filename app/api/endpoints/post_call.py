from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import json
import os
from app.core.config import settings

router = APIRouter()

class CallAnalysis(BaseModel):
    session_id: str
    start_time: datetime
    end_time: datetime
    duration: float
    user_satisfaction: Optional[int]
    intent_fulfilled: bool
    conversation_flow: List[Dict]
    error_count: int
    resolution_status: str
    pending_actions: Optional[List[str]]

# In-memory storage for call analysis (replace with database in production)
call_analyses: Dict[str, CallAnalysis] = {}

@router.post("/analyze")
async def analyze_call(analysis: CallAnalysis):
    """Store call analysis data"""
    call_analyses[analysis.session_id] = analysis
    return {"message": "Call analysis stored successfully"}

@router.get("/analysis/{session_id}")
async def get_call_analysis(session_id: str):
    """Get analysis for a specific call"""
    analysis = call_analyses.get(session_id)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"No analysis found for session {session_id}")
    return analysis

@router.get("/analyses")
async def list_call_analyses(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_satisfaction: Optional[int] = None
):
    """List all call analyses with optional filters"""
    filtered_analyses = call_analyses.values()
    
    if start_date:
        filtered_analyses = [
            a for a in filtered_analyses
            if a.start_time >= start_date
        ]
    
    if end_date:
        filtered_analyses = [
            a for a in filtered_analyses
            if a.end_time <= end_date
        ]
    
    if min_satisfaction is not None:
        filtered_analyses = [
            a for a in filtered_analyses
            if a.user_satisfaction and a.user_satisfaction >= min_satisfaction
        ]
    
    return {"analyses": list(filtered_analyses)}

@router.get("/metrics")
async def get_metrics():
    """Get aggregated metrics from call analyses"""
    if not call_analyses:
        return {
            "total_calls": 0,
            "average_satisfaction": 0,
            "intent_fulfillment_rate": 0,
            "average_duration": 0,
            "error_rate": 0
        }
    
    total_calls = len(call_analyses)
    total_satisfaction = sum(
        a.user_satisfaction or 0
        for a in call_analyses.values()
        if a.user_satisfaction is not None
    )
    total_fulfilled = sum(
        1 for a in call_analyses.values()
        if a.intent_fulfilled
    )
    total_duration = sum(
        a.duration for a in call_analyses.values()
    )
    total_errors = sum(
        a.error_count for a in call_analyses.values()
    )
    
    return {
        "total_calls": total_calls,
        "average_satisfaction": total_satisfaction / total_calls if total_calls > 0 else 0,
        "intent_fulfillment_rate": total_fulfilled / total_calls if total_calls > 0 else 0,
        "average_duration": total_duration / total_calls if total_calls > 0 else 0,
        "error_rate": total_errors / total_calls if total_calls > 0 else 0
    }

@router.get("/pending-actions")
async def get_pending_actions():
    """Get all pending actions from call analyses"""
    pending_actions = []
    for analysis in call_analyses.values():
        if analysis.pending_actions:
            pending_actions.extend(analysis.pending_actions)
    
    return {"pending_actions": list(set(pending_actions))}

@router.get("/export")
async def export_analyses():
    """Export all call analyses to a JSON file"""
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"call_analyses_{timestamp}.json"
    filepath = os.path.join(export_dir, filename)
    
    with open(filepath, "w") as f:
        json.dump(
            {k: v.dict() for k, v in call_analyses.items()},
            f,
            indent=2,
            default=str
        )
    
    return {"message": f"Analyses exported to {filename}"} 