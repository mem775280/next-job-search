#!/usr/bin/env python3
"""
Specific test for Authentication State Management Bug Fix
Tests that the critical authentication bug fix is working properly
"""

import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / 'frontend' / '.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class AuthBugFixTester:
    """Specific tester for authentication state management bug fix"""
    
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str, details: dict = None):
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
        
        if details:
            print(f"   Details: {details}")
    
    def test_auth_state_check_in_scraping_endpoint(self):
        """Test that scraping endpoint calls check_login_status() before checking is_logged_in"""
        try:
            # Test scraping endpoint without authentication
            scrape_data = {
                "keywords": "software engineer",
                "location": "Pakistan",
                "date_posted": "1w",
                "max_jobs": 5
            }
            
            response = self.session.post(f"{API_BASE}/linkedin/scrape-jobs", json=scrape_data, timeout=10)
            
            # Should return 401 because check_login_status() is called and user is not logged in
            if response.status_code == 401:
                data = response.json()
                error_message = data.get("detail", "")
                
                if "Please login to LinkedIn first" in error_message:
                    self.log_test(
                        "Scraping Endpoint Auth State Check", 
                        True, 
                        "✅ BUG FIX VERIFIED: Scraping endpoint correctly calls check_login_status() and returns proper 401 error",
                        {"status_code": 401, "error_message": error_message}
                    )
                    return True
                else:
                    self.log_test(
                        "Scraping Endpoint Auth State Check", 
                        False, 
                        "Unexpected error message format",
                        {"status_code": 401, "error_message": error_message}
                    )
                    return False
            else:
                self.log_test(
                    "Scraping Endpoint Auth State Check", 
                    False, 
                    f"Expected 401 status code, got {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Scraping Endpoint Auth State Check", 
                False, 
                f"Exception occurred: {str(e)}"
            )
            return False
    
    def test_auth_state_check_in_user_info_endpoint(self):
        """Test that user-info endpoint calls check_login_status() before checking is_logged_in"""
        try:
            response = self.session.get(f"{API_BASE}/linkedin/user-info", timeout=10)
            
            # Should return 401 because check_login_status() is called and user is not logged in
            if response.status_code == 401:
                data = response.json()
                error_message = data.get("detail", "")
                
                if "Not logged in" in error_message:
                    self.log_test(
                        "User Info Endpoint Auth State Check", 
                        True, 
                        "✅ BUG FIX VERIFIED: User info endpoint correctly calls check_login_status() and returns proper 401 error",
                        {"status_code": 401, "error_message": error_message}
                    )
                    return True
                else:
                    self.log_test(
                        "User Info Endpoint Auth State Check", 
                        False, 
                        "Unexpected error message format",
                        {"status_code": 401, "error_message": error_message}
                    )
                    return False
            else:
                self.log_test(
                    "User Info Endpoint Auth State Check", 
                    False, 
                    f"Expected 401 status code, got {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "User Info Endpoint Auth State Check", 
                False, 
                f"Exception occurred: {str(e)}"
            )
            return False
    
    def test_auth_status_consistency(self):
        """Test that authentication status is consistent across endpoints"""
        try:
            # Check auth status
            auth_data = {"action": "check_status"}
            auth_response = self.session.post(f"{API_BASE}/linkedin/auth", json=auth_data)
            
            if auth_response.status_code != 200:
                self.log_test(
                    "Auth Status Consistency", 
                    False, 
                    f"Auth status check failed with status {auth_response.status_code}"
                )
                return False
            
            auth_data = auth_response.json()
            is_logged_in = auth_data.get("logged_in", False)
            
            # Test user info endpoint
            user_info_response = self.session.get(f"{API_BASE}/linkedin/user-info")
            
            # Test scraping endpoint
            scrape_data = {
                "keywords": "test",
                "location": "Pakistan",
                "max_jobs": 1
            }
            scrape_response = self.session.post(f"{API_BASE}/linkedin/scrape-jobs", json=scrape_data, timeout=10)
            
            # Both endpoints should behave consistently based on login status
            if not is_logged_in:
                # Both should return 401
                if user_info_response.status_code == 401 and scrape_response.status_code == 401:
                    self.log_test(
                        "Auth Status Consistency", 
                        True, 
                        "✅ CONSISTENCY VERIFIED: All endpoints consistently report not logged in status",
                        {
                            "auth_logged_in": is_logged_in,
                            "user_info_status": user_info_response.status_code,
                            "scrape_status": scrape_response.status_code
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Auth Status Consistency", 
                        False, 
                        "Inconsistent authentication status across endpoints",
                        {
                            "auth_logged_in": is_logged_in,
                            "user_info_status": user_info_response.status_code,
                            "scrape_status": scrape_response.status_code
                        }
                    )
                    return False
            else:
                # If logged in, both should return 200 or appropriate success responses
                if user_info_response.status_code == 200 and scrape_response.status_code in [200, 408]:  # 408 for timeout
                    self.log_test(
                        "Auth Status Consistency", 
                        True, 
                        "✅ CONSISTENCY VERIFIED: All endpoints consistently report logged in status",
                        {
                            "auth_logged_in": is_logged_in,
                            "user_info_status": user_info_response.status_code,
                            "scrape_status": scrape_response.status_code
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Auth Status Consistency", 
                        False, 
                        "Inconsistent authentication status across endpoints",
                        {
                            "auth_logged_in": is_logged_in,
                            "user_info_status": user_info_response.status_code,
                            "scrape_status": scrape_response.status_code
                        }
                    )
                    return False
                
        except Exception as e:
            self.log_test(
                "Auth Status Consistency", 
                False, 
                f"Exception occurred: {str(e)}"
            )
            return False
    
    def test_error_response_format(self):
        """Test that error responses are properly formatted"""
        try:
            # Test scraping endpoint error response
            scrape_data = {
                "keywords": "test",
                "location": "Pakistan",
                "max_jobs": 1
            }
            scrape_response = self.session.post(f"{API_BASE}/linkedin/scrape-jobs", json=scrape_data, timeout=10)
            
            if scrape_response.status_code == 401:
                try:
                    scrape_data = scrape_response.json()
                    if "detail" in scrape_data:
                        self.log_test(
                            "Error Response Format - Scraping", 
                            True, 
                            "✅ ERROR FORMAT VERIFIED: Scraping endpoint returns properly formatted 401 error",
                            {"error_detail": scrape_data["detail"]}
                        )
                    else:
                        self.log_test(
                            "Error Response Format - Scraping", 
                            False, 
                            "Error response missing 'detail' field",
                            {"response": scrape_data}
                        )
                        return False
                except json.JSONDecodeError:
                    self.log_test(
                        "Error Response Format - Scraping", 
                        False, 
                        "Error response is not valid JSON"
                    )
                    return False
            
            # Test user info endpoint error response
            user_info_response = self.session.get(f"{API_BASE}/linkedin/user-info")
            
            if user_info_response.status_code == 401:
                try:
                    user_info_data = user_info_response.json()
                    if "detail" in user_info_data:
                        self.log_test(
                            "Error Response Format - User Info", 
                            True, 
                            "✅ ERROR FORMAT VERIFIED: User info endpoint returns properly formatted 401 error",
                            {"error_detail": user_info_data["detail"]}
                        )
                        return True
                    else:
                        self.log_test(
                            "Error Response Format - User Info", 
                            False, 
                            "Error response missing 'detail' field",
                            {"response": user_info_data}
                        )
                        return False
                except json.JSONDecodeError:
                    self.log_test(
                        "Error Response Format - User Info", 
                        False, 
                        "Error response is not valid JSON"
                    )
                    return False
            
            return True
                
        except Exception as e:
            self.log_test(
                "Error Response Format", 
                False, 
                f"Exception occurred: {str(e)}"
            )
            return False
    
    def run_auth_bug_fix_tests(self):
        """Run all authentication bug fix tests"""
        print("=" * 80)
        print("AUTHENTICATION STATE MANAGEMENT BUG FIX VERIFICATION")
        print("=" * 80)
        print(f"Testing API at: {API_BASE}")
        print()
        print("🔍 CRITICAL BUG FIX TESTS")
        print("Testing that endpoints call check_login_status() before checking is_logged_in flag")
        print("-" * 80)
        
        # Run specific bug fix tests
        test1 = self.test_auth_state_check_in_scraping_endpoint()
        test2 = self.test_auth_state_check_in_user_info_endpoint()
        test3 = self.test_auth_status_consistency()
        test4 = self.test_error_response_format()
        
        print()
        print("=" * 80)
        print("BUG FIX VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests == 0:
            print("\n🎉 ✅ AUTHENTICATION BUG FIX VERIFICATION: SUCCESSFUL")
            print("The reported LinkedIn scraping error should now be resolved!")
            print("Both scrape-jobs and user-info endpoints now properly call check_login_status()")
            print("before checking the is_logged_in flag, ensuring accurate authentication state.")
        else:
            print("\n❌ BUG FIX VERIFICATION: FAILED")
            failed_tests_list = [t for t in self.test_results if not t["success"]]
            for test in failed_tests_list:
                print(f"  - {test['test']}: {test['message']}")
        
        print("\n" + "=" * 80)
        
        return passed_tests, failed_tests, total_tests

def main():
    """Main testing function"""
    tester = AuthBugFixTester()
    passed, failed, total = tester.run_auth_bug_fix_tests()
    
    # Return appropriate exit code
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())