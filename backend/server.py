from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import csv
import io
import tempfile
from linkedin_scraper import get_scraper_instance, cleanup_scraper


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class LinkedInLoginRequest(BaseModel):
    action: str  # 'login', 'check_status', 'logout'

class LinkedInScrapingRequest(BaseModel):
    keywords: str
    location: str = "Pakistan"
    date_posted: str = "1w"  # 24h, 3d, 1w, 2w, 1m
    experience_level: Optional[str] = None  # internship, entry, associate, mid, director, executive
    job_type: Optional[str] = None  # full-time, part-time, contract, temporary, volunteer, internship
    remote: bool = False
    salary_min: Optional[str] = None
    max_jobs: int = 50

class ScrapedJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    company: str
    location: str
    url: str
    posted_date: str
    description: str = "N/A"
    salary: str = "N/A" 
    emails: List[str] = []
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "LinkedIn Job Scraper API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# LinkedIn Authentication Endpoints
@api_router.post("/linkedin/auth")
async def linkedin_auth(request: LinkedInLoginRequest):
    """Handle LinkedIn authentication actions"""
    try:
        scraper = await get_scraper_instance()
        
        if request.action == "check_status":
            # Check if already logged in
            is_logged_in = await scraper.check_login_status()
            if is_logged_in:
                user_info = await scraper.get_user_info()
                return {
                    "success": True,
                    "logged_in": True,
                    "message": "Already logged in",
                    "user": user_info
                }
            else:
                return {
                    "success": True,
                    "logged_in": False,
                    "message": "Not logged in"
                }
        
        elif request.action == "login":
            # Try to load existing session first
            session_loaded = await scraper.load_session()
            if session_loaded:
                user_info = await scraper.get_user_info()
                return {
                    "success": True,
                    "logged_in": True,
                    "message": "Session restored successfully",
                    "user": user_info
                }
            else:
                # Initiate manual login process
                result = await scraper.wait_for_manual_login()
                return result
        
        elif request.action == "logout":
            result = await scraper.logout()
            return result
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Valid actions are: check_status, login, logout")
            
    except Exception as e:
        logging.error(f"LinkedIn auth error: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

@api_router.get("/linkedin/user-info")
async def get_linkedin_user_info():
    """Get current user information"""
    try:
        scraper = await get_scraper_instance()
        
        if not scraper.is_logged_in:
            raise HTTPException(status_code=401, detail="Not logged in")
        
        user_info = await scraper.get_user_info()
        
        # Check if there was an error getting user info
        if "error" in user_info:
            raise HTTPException(status_code=500, detail=f"Browser error: {user_info['error']}")
        
        return {
            "success": True,
            "user": user_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User info error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")

# LinkedIn Job Scraping Endpoints
@api_router.post("/linkedin/scrape-jobs")
async def scrape_linkedin_jobs(request: LinkedInScrapingRequest, background_tasks: BackgroundTasks):
    """Scrape LinkedIn jobs with advanced filtering"""
    try:
        scraper = await get_scraper_instance()
        
        if not scraper.is_logged_in:
            raise HTTPException(status_code=401, detail="Please login to LinkedIn first")
        
        # Convert request to filters
        filters = {
            "keywords": request.keywords,
            "location": request.location,
            "date_posted": request.date_posted,
            "experience_level": request.experience_level,
            "job_type": request.job_type,
            "remote": request.remote,
            "salary_min": request.salary_min
        }
        
        # Scrape jobs
        result = await scraper.scrape_jobs(filters, max_jobs=request.max_jobs)
        
        if result["success"]:
            # Save scraped jobs to database
            scraped_jobs = []
            for job_data in result["jobs"]:
                job_obj = ScrapedJob(
                    title=job_data.get("title", "N/A"),
                    company=job_data.get("company", "N/A"),
                    location=job_data.get("location", "N/A"),
                    url=job_data.get("url", "N/A"),
                    posted_date=job_data.get("posted_date", "N/A"),
                    description=job_data.get("description", "N/A"),
                    salary=job_data.get("salary", "N/A"),
                    emails=job_data.get("emails", [])
                )
                scraped_jobs.append(job_obj)
            
            # Insert into database
            if scraped_jobs:
                job_dicts = [job.dict() for job in scraped_jobs]
                await db.scraped_jobs.insert_many(job_dicts)
            
            return {
                "success": True,
                "message": result["message"],
                "jobs": [job.dict() for job in scraped_jobs],
                "total_found": len(scraped_jobs)
            }
        else:
            return result
            
    except Exception as e:
        logging.error(f"Scraping error: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@api_router.get("/linkedin/jobs")
async def get_scraped_jobs(limit: int = 100, offset: int = 0):
    """Get scraped jobs from database"""
    try:
        jobs = await db.scraped_jobs.find().skip(offset).limit(limit).to_list(limit)
        total_count = await db.scraped_jobs.count_documents({})
        
        return {
            "success": True,
            "jobs": jobs,
            "total": total_count,
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        logging.error(f"Database query error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve jobs: {str(e)}")

@api_router.get("/linkedin/jobs/export-csv")
async def export_jobs_csv():
    """Export scraped jobs to CSV"""
    try:
        jobs = await db.scraped_jobs.find().to_list(1000)
        
        if not jobs:
            raise HTTPException(status_code=404, detail="No jobs found to export")
        
        # Create temporary CSV file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        
        fieldnames = ['title', 'company', 'location', 'url', 'posted_date', 'description', 'salary', 'emails', 'scraped_at']
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        
        writer.writeheader()
        for job in jobs:
            # Prepare job data for CSV
            csv_job = {
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'location': job.get('location', ''),
                'url': job.get('url', ''),
                'posted_date': job.get('posted_date', ''),
                'description': job.get('description', ''),
                'salary': job.get('salary', ''),
                'emails': ', '.join(job.get('emails', [])),
                'scraped_at': job.get('scraped_at', '')
            }
            writer.writerow(csv_job)
        
        temp_file.close()
        
        return FileResponse(
            path=temp_file.name,
            filename=f"linkedin_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        logging.error(f"CSV export error: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@api_router.delete("/linkedin/jobs")
async def clear_scraped_jobs():
    """Clear all scraped jobs from database"""
    try:
        result = await db.scraped_jobs.delete_many({})
        return {
            "success": True,
            "message": f"Deleted {result.deleted_count} jobs"
        }
        
    except Exception as e:
        logging.error(f"Clear jobs error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear jobs: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize application"""
    logger.info("LinkedIn Job Scraper API started")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Cleanup resources"""
    await cleanup_scraper()
    client.close()
    logger.info("Application shutdown complete")
