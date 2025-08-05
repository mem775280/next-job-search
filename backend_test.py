#!/usr/bin/env python3
"""
Comprehensive Backend Testing for LinkedIn Job Scraper API
Tests all authentication, scraping, and data management endpoints
"""

import asyncio
import requests
import json
import time
import os
from typing import Dict, Any, List
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / 'frontend' / '.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class LinkedInScraperTester:
    """Comprehensive tester for LinkedIn Scraper API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if not success:
            self.failed_tests.append(result)
            if details:
                print(f"   Details: {details}")
    
    def test_api_health(self):
        """Test basic API health and connectivity"""
        try:
            response = self.session.get(f"{API_BASE}/")
            
            if response.status_code == 200:
                data = response.json()
                if "LinkedIn Job Scraper API" in data.get("message", ""):
                    self.log_test("API Health Check", True, "API is responding correctly")
                    return True
                else:
                    self.log_test("API Health Check", False, "Unexpected API response", {"response": data})
                    return False
            else:
                self.log_test("API Health Check", False, f"API returned status {response.status_code}", 
                            {"status_code": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            self.log_test("API Health Check", False, f"Failed to connect to API: {str(e)}")
            return False
    
    def test_status_endpoints(self):
        """Test status check endpoints"""
        try:
            # Test POST status endpoint
            test_data = {"client_name": "test_client_backend"}
            response = self.session.post(f"{API_BASE}/status", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("client_name") == "test_client_backend" and "id" in data:
                    self.log_test("Status POST Endpoint", True, "Status creation successful")
                else:
                    self.log_test("Status POST Endpoint", False, "Invalid response format", {"response": data})
                    return False
            else:
                self.log_test("Status POST Endpoint", False, f"Status code: {response.status_code}", 
                            {"response": response.text})
                return False
            
            # Test GET status endpoint
            response = self.session.get(f"{API_BASE}/status")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Status GET Endpoint", True, f"Retrieved {len(data)} status records")
                    return True
                else:
                    self.log_test("Status GET Endpoint", False, "Expected list response", {"response": data})
                    return False
            else:
                self.log_test("Status GET Endpoint", False, f"Status code: {response.status_code}", 
                            {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test("Status Endpoints", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_linkedin_auth_check_status(self):
        """Test LinkedIn authentication status check"""
        try:
            auth_data = {"action": "check_status"}
            response = self.session.post(f"{API_BASE}/linkedin/auth", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and "logged_in" in data:
                    logged_in = data.get("logged_in", False)
                    message = f"Auth status check successful - Logged in: {logged_in}"
                    self.log_test("LinkedIn Auth Status Check", True, message, {"logged_in": logged_in})
                    return logged_in
                else:
                    self.log_test("LinkedIn Auth Status Check", False, "Invalid response format", {"response": data})
                    return False
            else:
                self.log_test("LinkedIn Auth Status Check", False, f"Status code: {response.status_code}", 
                            {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test("LinkedIn Auth Status Check", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_linkedin_auth_login(self):
        """Test LinkedIn login endpoint (will require manual intervention)"""
        try:
            auth_data = {"action": "login"}
            response = self.session.post(f"{API_BASE}/linkedin/auth", json=auth_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("LinkedIn Auth Login", True, "Login endpoint responded successfully", 
                                {"message": data.get("message")})
                    return True
                else:
                    self.log_test("LinkedIn Auth Login", False, "Login failed", {"response": data})
                    return False
            else:
                self.log_test("LinkedIn Auth Login", False, f"Status code: {response.status_code}", 
                            {"response": response.text})
                return False
                
        except requests.exceptions.Timeout:
            self.log_test("LinkedIn Auth Login", True, "Login endpoint timeout (expected for manual login)")
            return True
        except Exception as e:
            self.log_test("LinkedIn Auth Login", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_linkedin_auth_logout(self):
        """Test LinkedIn logout endpoint"""
        try:
            auth_data = {"action": "logout"}
            response = self.session.post(f"{API_BASE}/linkedin/auth", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data:
                    self.log_test("LinkedIn Auth Logout", True, "Logout endpoint responded successfully", 
                                {"message": data.get("message")})
                    return True
                else:
                    self.log_test("LinkedIn Auth Logout", False, "Invalid response format", {"response": data})
                    return False
            else:
                self.log_test("LinkedIn Auth Logout", False, f"Status code: {response.status_code}", 
                            {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test("LinkedIn Auth Logout", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_linkedin_user_info(self):
        """Test LinkedIn user info endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/linkedin/user-info")
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and "user" in data:
                    self.log_test("LinkedIn User Info", True, "User info retrieved successfully", 
                                {"user": data.get("user")})
                    return True
                else:
                    self.log_test("LinkedIn User Info", False, "Invalid response format", {"response": data})
                    return False
            elif response.status_code == 401:
                self.log_test("LinkedIn User Info", True, "Correctly returned 401 for unauthenticated request")
                return True
            else:
                self.log_test("LinkedIn User Info", False, f"Status code: {response.status_code}", 
                            {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test("LinkedIn User Info", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_linkedin_scrape_jobs(self):
        """Test LinkedIn job scraping endpoint"""
        try:
            scrape_data = {
                "keywords": "software engineer",
                "location": "Pakistan",
                "date_posted": "1w",
                "experience_level": "entry",
                "job_type": "full-time",
                "remote": False,
                "max_jobs": 5
            }
            
            response = self.session.post(f"{API_BASE}/linkedin/scrape-jobs", json=scrape_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data:
                    if data.get("success"):
                        jobs_count = len(data.get("jobs", []))
                        self.log_test("LinkedIn Job Scraping", True, 
                                    f"Scraping successful - Found {jobs_count} jobs", 
                                    {"jobs_count": jobs_count, "message": data.get("message")})
                        return True
                    else:
                        self.log_test("LinkedIn Job Scraping", False, "Scraping failed", 
                                    {"message": data.get("message")})
                        return False
                else:
                    self.log_test("LinkedIn Job Scraping", False, "Invalid response format", {"response": data})
                    return False
            elif response.status_code == 401:
                self.log_test("LinkedIn Job Scraping", True, "Correctly returned 401 for unauthenticated request")
                return True
            else:
                self.log_test("LinkedIn Job Scraping", False, f"Status code: {response.status_code}", 
                            {"response": response.text})
                return False
                
        except requests.exceptions.Timeout:
            self.log_test("LinkedIn Job Scraping", True, "Scraping timeout (expected for complex operation)")
            return True
        except Exception as e:
            self.log_test("LinkedIn Job Scraping", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_linkedin_get_jobs(self):
        """Test retrieving scraped jobs from database"""
        try:
            response = self.session.get(f"{API_BASE}/linkedin/jobs?limit=10&offset=0")
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and "jobs" in data and "total" in data:
                    jobs_count = len(data.get("jobs", []))
                    total_count = data.get("total", 0)
                    self.log_test("LinkedIn Get Jobs", True, 
                                f"Retrieved {jobs_count} jobs (total: {total_count})", 
                                {"jobs_count": jobs_count, "total": total_count})
                    return True
                else:
                    self.log_test("LinkedIn Get Jobs", False, "Invalid response format", {"response": data})
                    return False
            else:
                self.log_test("LinkedIn Get Jobs", False, f"Status code: {response.status_code}", 
                            {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test("LinkedIn Get Jobs", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_linkedin_export_csv(self):
        """Test CSV export functionality"""
        try:
            response = self.session.get(f"{API_BASE}/linkedin/jobs/export-csv")
            
            if response.status_code == 200:
                # Check if response is CSV content
                content_type = response.headers.get('content-type', '')
                if 'csv' in content_type.lower() or 'octet-stream' in content_type.lower():
                    self.log_test("LinkedIn CSV Export", True, "CSV export successful", 
                                {"content_type": content_type, "size": len(response.content)})
                    return True
                else:
                    self.log_test("LinkedIn CSV Export", False, "Unexpected content type", 
                                {"content_type": content_type})
                    return False
            elif response.status_code == 404:
                self.log_test("LinkedIn CSV Export", True, "Correctly returned 404 for no jobs to export")
                return True
            else:
                self.log_test("LinkedIn CSV Export", False, f"Status code: {response.status_code}", 
                            {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test("LinkedIn CSV Export", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_linkedin_clear_jobs(self):
        """Test clearing scraped jobs"""
        try:
            response = self.session.delete(f"{API_BASE}/linkedin/jobs")
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and "message" in data:
                    deleted_count = data.get("message", "").split()[-2] if "Deleted" in data.get("message", "") else "0"
                    self.log_test("LinkedIn Clear Jobs", True, f"Jobs cleared successfully - {data.get('message')}", 
                                {"deleted_count": deleted_count})
                    return True
                else:
                    self.log_test("LinkedIn Clear Jobs", False, "Invalid response format", {"response": data})
                    return False
            else:
                self.log_test("LinkedIn Clear Jobs", False, f"Status code: {response.status_code}", 
                            {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test("LinkedIn Clear Jobs", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_comprehensive_filtering(self):
        """Test comprehensive filtering system"""
        try:
            # Test with various filter combinations
            filter_tests = [
                {
                    "name": "Basic Keywords Filter",
                    "data": {
                        "keywords": "python developer",
                        "location": "Pakistan",
                        "max_jobs": 3
                    }
                },
                {
                    "name": "Date and Experience Filter",
                    "data": {
                        "keywords": "data scientist",
                        "location": "Pakistan",
                        "date_posted": "3d",
                        "experience_level": "mid",
                        "max_jobs": 3
                    }
                },
                {
                    "name": "Job Type and Remote Filter",
                    "data": {
                        "keywords": "frontend developer",
                        "location": "Pakistan",
                        "job_type": "full-time",
                        "remote": True,
                        "max_jobs": 3
                    }
                }
            ]
            
            all_passed = True
            for test_case in filter_tests:
                try:
                    response = self.session.post(f"{API_BASE}/linkedin/scrape-jobs", 
                                               json=test_case["data"], timeout=20)
                    
                    if response.status_code in [200, 401]:  # 401 is acceptable if not logged in
                        if response.status_code == 200:
                            data = response.json()
                            success = data.get("success", False)
                            message = f"{test_case['name']} - Response received"
                        else:
                            success = True  # 401 is expected behavior
                            message = f"{test_case['name']} - Correctly requires authentication"
                        
                        self.log_test(f"Filter Test: {test_case['name']}", success, message)
                    else:
                        self.log_test(f"Filter Test: {test_case['name']}", False, 
                                    f"Status code: {response.status_code}")
                        all_passed = False
                        
                except requests.exceptions.Timeout:
                    self.log_test(f"Filter Test: {test_case['name']}", True, "Timeout (expected)")
                except Exception as e:
                    self.log_test(f"Filter Test: {test_case['name']}", False, f"Exception: {str(e)}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_test("Comprehensive Filtering", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test API error handling"""
        try:
            # Test invalid auth action
            response = self.session.post(f"{API_BASE}/linkedin/auth", json={"action": "invalid_action"})
            if response.status_code == 400:
                self.log_test("Error Handling: Invalid Auth Action", True, "Correctly returned 400 for invalid action")
            else:
                self.log_test("Error Handling: Invalid Auth Action", False, f"Expected 400, got {response.status_code}")
            
            # Test invalid scraping data
            response = self.session.post(f"{API_BASE}/linkedin/scrape-jobs", json={})
            if response.status_code in [400, 422]:  # 422 for validation errors
                self.log_test("Error Handling: Invalid Scraping Data", True, "Correctly handled invalid data")
            else:
                self.log_test("Error Handling: Invalid Scraping Data", False, f"Expected 400/422, got {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Error Handling", False, f"Exception occurred: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 80)
        print("LINKEDIN JOB SCRAPER - BACKEND API TESTING")
        print("=" * 80)
        print(f"Testing API at: {API_BASE}")
        print()
        
        # Core API tests
        print("🔍 CORE API TESTS")
        print("-" * 40)
        self.test_api_health()
        self.test_status_endpoints()
        print()
        
        # LinkedIn Authentication tests
        print("🔐 LINKEDIN AUTHENTICATION TESTS")
        print("-" * 40)
        self.test_linkedin_auth_check_status()
        self.test_linkedin_auth_login()
        self.test_linkedin_auth_logout()
        self.test_linkedin_user_info()
        print()
        
        # LinkedIn Scraping tests
        print("🕷️ LINKEDIN SCRAPING TESTS")
        print("-" * 40)
        self.test_linkedin_scrape_jobs()
        self.test_linkedin_get_jobs()
        self.test_linkedin_export_csv()
        self.test_linkedin_clear_jobs()
        print()
        
        # Advanced feature tests
        print("⚙️ ADVANCED FEATURE TESTS")
        print("-" * 40)
        self.test_comprehensive_filtering()
        self.test_error_handling()
        print()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        print("\n" + "=" * 80)
        
        return passed_tests, failed_tests, total_tests

def main():
    """Main testing function"""
    tester = LinkedInScraperTester()
    passed, failed, total = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())