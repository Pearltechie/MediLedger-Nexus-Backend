#!/usr/bin/env python3
"""
MediLedger Nexus Comprehensive API Demo
Demonstrates all key features including validation, AI diagnostics, HCS-10, and error handling
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
import uuid


class MediLedgerComprehensiveDemo:
    """Comprehensive demo client for MediLedger Nexus API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        self.auth_token = None
        self.user_data = {}
        self.demo_results = []
        self.test_scenarios = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def _log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.demo_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_health_check(self) -> bool:
        """Test API health check"""
        print("\n🏥 Testing API Health Check...")
        try:
            response = await self.client.get("/health")
            if response.status_code == 200:
                data = response.json()
                self._log_result("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self._log_result("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self._log_result("Health Check", False, f"Error: {str(e)}")
            return False
    
    async def test_user_registration_validation(self) -> bool:
        """Test user registration with various validation scenarios"""
        print("\n🔐 Testing User Registration Validation...")
        
        test_cases = [
            {
                "name": "Valid Registration",
                "data": {
                    "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                    "password": "SecurePassword123!",
                    "full_name": "John Doe",
                    "hedera_account_id": "0.0.123456"
                },
                "should_succeed": True
            },
            {
                "name": "Invalid Email",
                "data": {
                    "email": "invalid-email",
                    "password": "SecurePassword123!",
                    "full_name": "John Doe"
                },
                "should_succeed": False
            },
            {
                "name": "Weak Password",
                "data": {
                    "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                    "password": "weak",
                    "full_name": "John Doe"
                },
                "should_succeed": False
            },
            {
                "name": "Invalid Hedera Account",
                "data": {
                    "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                    "password": "SecurePassword123!",
                    "full_name": "John Doe",
                    "hedera_account_id": "invalid-account"
                },
                "should_succeed": False
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                response = await self.client.post("/api/v1/auth/register", json=test_case["data"])
                
                if test_case["should_succeed"]:
                    if response.status_code == 200:
                        self._log_result(f"Registration - {test_case['name']}", True, "Validation passed")
                        # Store valid user for later tests
                        if test_case["name"] == "Valid Registration":
                            self.user_data = test_case["data"]
                    else:
                        self._log_result(f"Registration - {test_case['name']}", False, f"Expected success but got {response.status_code}")
                        all_passed = False
                else:
                    if response.status_code != 200:
                        self._log_result(f"Registration - {test_case['name']}", True, "Validation correctly failed")
                    else:
                        self._log_result(f"Registration - {test_case['name']}", False, "Expected failure but succeeded")
                        all_passed = False
                        
            except Exception as e:
                self._log_result(f"Registration - {test_case['name']}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    async def test_authentication_flow(self) -> bool:
        """Test complete authentication flow"""
        print("\n🔑 Testing Authentication Flow...")
        
        if not self.user_data:
            self._log_result("Authentication Flow", False, "No valid user data available")
            return False
        
        try:
            # Test login
            login_data = {
                "username": self.user_data["email"],
                "password": self.user_data["password"]
            }
            
            response = await self.client.post("/api/v1/auth/token", data=login_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data["access_token"]
                self._log_result("Login", True, "Token received")
                
                # Test getting current user
                response = await self.client.get("/api/v1/auth/me", headers=self._get_headers())
                if response.status_code == 200:
                    user_info = response.json()
                    self._log_result("Get Current User", True, f"User: {user_info.get('email')}")
                    
                    # Test token refresh
                    response = await self.client.post("/api/v1/auth/refresh", headers=self._get_headers())
                    if response.status_code == 200:
                        self._log_result("Token Refresh", True, "New token received")
                        return True
                    else:
                        self._log_result("Token Refresh", False, f"Status: {response.status_code}")
                        return False
                else:
                    self._log_result("Get Current User", False, f"Status: {response.status_code}")
                    return False
            else:
                self._log_result("Login", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self._log_result("Authentication Flow", False, f"Error: {str(e)}")
            return False
    
    async def test_health_vault_management(self) -> bool:
        """Test health vault creation and management"""
        print("\n🏥 Testing Health Vault Management...")
        
        if not self.auth_token:
            self._log_result("Health Vault Management", False, "No authentication token")
            return False
        
        try:
            # Create health vault
            vault_data = {
                "name": "Primary Health Vault",
                "description": "Main vault for medical records",
                "encryption_enabled": True,
                "zk_proofs_enabled": True,
                "privacy_level": "high"
            }
            
            response = await self.client.post(
                "/api/v1/vault/create",
                json=vault_data,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                vault_info = response.json()
                vault_id = vault_info.get("id")
                self._log_result("Create Health Vault", True, f"Vault ID: {vault_id}")
                
                # Get user vaults
                response = await self.client.get("/api/v1/vault/", headers=self._get_headers())
                if response.status_code == 200:
                    vaults = response.json()
                    self._log_result("List Health Vaults", True, f"Found {len(vaults)} vaults")
                    
                    # Get specific vault
                    if vault_id:
                        response = await self.client.get(f"/api/v1/vault/{vault_id}", headers=self._get_headers())
                        if response.status_code == 200:
                            self._log_result("Get Specific Vault", True, "Vault details retrieved")
                            return True
                        else:
                            self._log_result("Get Specific Vault", False, f"Status: {response.status_code}")
                            return False
                else:
                    self._log_result("List Health Vaults", False, f"Status: {response.status_code}")
                    return False
            else:
                self._log_result("Create Health Vault", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self._log_result("Health Vault Management", False, f"Error: {str(e)}")
            return False
    
    async def test_ai_diagnostics_and_hcs10(self) -> bool:
        """Test AI diagnostics with HCS-10 integration"""
        print("\n🤖 Testing AI Diagnostics & HCS-10...")
        
        if not self.auth_token:
            self._log_result("AI Diagnostics", False, "No authentication token")
            return False
        
        try:
            # Register AI agent
            agent_data = {
                "name": "Personal Health AI",
                "agent_type": "diagnostic_agent",
                "capabilities": ["diagnosis", "health_insights", "emergency_response"],
                "hcs_topic_id": f"0.0.{random.randint(100000, 999999)}",
                "profile_metadata": {
                    "specialization": "general_medicine",
                    "confidence_threshold": 0.8
                }
            }
            
            response = await self.client.post(
                "/api/v1/ai/register-agent",
                json=agent_data,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                agent_info = response.json()
                agent_id = agent_info.get("agent_id")
                self._log_result("Register AI Agent", True, f"Agent ID: {agent_id}")
                
                # Request AI diagnosis
                diagnosis_data = {
                    "symptoms": ["chest_pain", "shortness_of_breath", "fatigue"],
                    "medical_history": {
                        "age": 45,
                        "gender": "male",
                        "conditions": ["hypertension"],
                        "medications": ["lisinopril"],
                        "allergies": ["penicillin"]
                    },
                    "use_federated_learning": True,
                    "privacy_level": "high",
                    "urgency_level": "moderate"
                }
                
                response = await self.client.post(
                    "/api/v1/ai/diagnose",
                    json=diagnosis_data,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    diagnosis_result = response.json()
                    self._log_result("AI Diagnosis", True, f"Diagnosis: {diagnosis_result.get('primary_diagnosis')}")
                    
                    # Get AI insights
                    response = await self.client.get("/api/v1/ai/insights", headers=self._get_headers())
                    if response.status_code == 200:
                        self._log_result("AI Insights", True, "Health insights retrieved")
                        return True
                    else:
                        self._log_result("AI Insights", False, f"Status: {response.status_code}")
                        return False
                else:
                    self._log_result("AI Diagnosis", False, f"Status: {response.status_code}")
                    return False
            else:
                self._log_result("Register AI Agent", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self._log_result("AI Diagnostics", False, f"Error: {str(e)}")
            return False
    
    async def test_consent_management(self) -> bool:
        """Test consent management and tokenization"""
        print("\n📋 Testing Consent Management...")
        
        if not self.auth_token:
            self._log_result("Consent Management", False, "No authentication token")
            return False
        
        try:
            # Grant consent
            consent_data = {
                "provider_account_id": f"0.0.{random.randint(100000, 999999)}",
                "record_types": ["lab_results", "imaging", "vital_signs"],
                "duration_hours": 24,
                "compensation_rate": 5.0,
                "purpose": "Medical diagnosis and treatment",
                "privacy_level": "high"
            }
            
            response = await self.client.post(
                "/api/v1/consent/grant",
                json=consent_data,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                consent_info = response.json()
                consent_id = consent_info.get("id")
                self._log_result("Grant Consent", True, f"Consent ID: {consent_id}")
                
                # Get user consents
                response = await self.client.get("/api/v1/consent/", headers=self._get_headers())
                if response.status_code == 200:
                    consents = response.json()
                    self._log_result("List Consents", True, f"Found {len(consents)} consents")
                    
                    # Get consent earnings
                    if consent_id:
                        response = await self.client.get(f"/api/v1/consent/{consent_id}/earnings", headers=self._get_headers())
                        if response.status_code == 200:
                            earnings = response.json()
                            self._log_result("Consent Earnings", True, f"Earnings: {earnings.get('total_earned', 0)} HEAL")
                            return True
                        else:
                            self._log_result("Consent Earnings", False, f"Status: {response.status_code}")
                            return False
                else:
                    self._log_result("List Consents", False, f"Status: {response.status_code}")
                    return False
            else:
                self._log_result("Grant Consent", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self._log_result("Consent Management", False, f"Error: {str(e)}")
            return False
    
    async def test_federated_learning(self) -> bool:
        """Test federated learning participation"""
        print("\n🧠 Testing Federated Learning...")
        
        if not self.auth_token:
            self._log_result("Federated Learning", False, "No authentication token")
            return False
        
        try:
            # Join federated learning study
            fl_data = {
                "study_type": "cardiovascular_disease",
                "data_contribution": "anonymized_records",
                "min_participants": 3,
                "max_rounds": 10,
                "privacy_budget": 1.0
            }
            
            response = await self.client.post(
                "/api/v1/ai/federated-learning/join",
                json=fl_data,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                fl_result = response.json()
                round_id = fl_result.get("round_id")
                self._log_result("Join Federated Learning", True, f"Round ID: {round_id}")
                
                # Get federated learning rounds
                response = await self.client.get("/api/v1/ai/federated-learning/rounds", headers=self._get_headers())
                if response.status_code == 200:
                    rounds = response.json()
                    self._log_result("List FL Rounds", True, f"Found {len(rounds)} rounds")
                    return True
                else:
                    self._log_result("List FL Rounds", False, f"Status: {response.status_code}")
                    return False
            else:
                self._log_result("Join Federated Learning", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self._log_result("Federated Learning", False, f"Error: {str(e)}")
            return False
    
    async def test_emergency_access(self) -> bool:
        """Test emergency access protocol"""
        print("\n🚨 Testing Emergency Access...")
        
        if not self.auth_token:
            self._log_result("Emergency Access", False, "No authentication token")
            return False
        
        try:
            # Update emergency profile first
            emergency_profile = {
                "blood_type": "O+",
                "allergies": ["penicillin", "latex"],
                "current_medications": ["lisinopril", "metformin"],
                "medical_conditions": ["hypertension", "diabetes"],
                "emergency_contact": {
                    "name": "Jane Doe",
                    "phone": "+1234567890",
                    "relationship": "spouse",
                    "email": "jane.doe@example.com"
                }
            }
            
            response = await self.client.put(
                "/api/v1/emergency/profile",
                json=emergency_profile,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                self._log_result("Update Emergency Profile", True, "Profile updated")
                
                # Test emergency access (simulate provider request)
                emergency_request = {
                    "patient_identifier": self.user_data.get("email"),
                    "emergency_type": "cardiac_arrest",
                    "requester_credentials": "EMT_LICENSE_12345",
                    "location": "General Hospital ER",
                    "urgency_level": "critical"
                }
                
                response = await self.client.post(
                    "/api/v1/emergency/access",
                    json=emergency_request,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    emergency_data = response.json()
                    self._log_result("Emergency Access", True, f"Blood type: {emergency_data.get('blood_type')}")
                    return True
                else:
                    self._log_result("Emergency Access", False, f"Status: {response.status_code}")
                    return False
            else:
                self._log_result("Update Emergency Profile", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self._log_result("Emergency Access", False, f"Error: {str(e)}")
            return False
    
    async def test_research_participation(self) -> bool:
        """Test research study participation"""
        print("\n🔬 Testing Research Participation...")
        
        if not self.auth_token:
            self._log_result("Research Participation", False, "No authentication token")
            return False
        
        try:
            # Get available studies
            response = await self.client.get("/api/v1/research/studies", headers=self._get_headers())
            
            if response.status_code == 200:
                studies = response.json()
                self._log_result("List Research Studies", True, f"Found {len(studies)} studies")
                
                # Participate in a study
                participation_data = {
                    "study_id": f"study_{uuid.uuid4().hex[:8]}",
                    "data_types": ["vital_signs", "lab_results"],
                    "anonymization_level": "high",
                    "compensation_expected": 10.0
                }
                
                response = await self.client.post(
                    "/api/v1/research/participate",
                    json=participation_data,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    participation_result = response.json()
                    self._log_result("Research Participation", True, f"Participation ID: {participation_result.get('id')}")
                    return True
                else:
                    self._log_result("Research Participation", False, f"Status: {response.status_code}")
                    return False
            else:
                self._log_result("List Research Studies", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self._log_result("Research Participation", False, f"Error: {str(e)}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling and edge cases"""
        print("\n⚠️ Testing Error Handling...")
        
        error_tests = [
            {
                "name": "Unauthorized Access",
                "method": "GET",
                "url": "/api/v1/vault/",
                "headers": {},
                "expected_status": 401
            },
            {
                "name": "Invalid Endpoint",
                "method": "GET", 
                "url": "/api/v1/nonexistent",
                "headers": self._get_headers(),
                "expected_status": 404
            },
            {
                "name": "Invalid JSON",
                "method": "POST",
                "url": "/api/v1/vault/create",
                "headers": self._get_headers(),
                "data": "invalid json",
                "expected_status": 422
            }
        ]
        
        all_passed = True
        
        for test in error_tests:
            try:
                if test["method"] == "GET":
                    response = await self.client.get(test["url"], headers=test["headers"])
                elif test["method"] == "POST":
                    if "data" in test:
                        response = await self.client.post(test["url"], content=test["data"], headers=test["headers"])
                    else:
                        response = await self.client.post(test["url"], headers=test["headers"])
                
                if response.status_code == test["expected_status"]:
                    self._log_result(f"Error Handling - {test['name']}", True, f"Expected {test['expected_status']}")
                else:
                    self._log_result(f"Error Handling - {test['name']}", False, f"Expected {test['expected_status']}, got {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self._log_result(f"Error Handling - {test['name']}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    async def run_comprehensive_demo(self):
        """Run all demo tests"""
        print("🚀 Starting MediLedger Nexus Comprehensive API Demo")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run all test scenarios
        test_methods = [
            self.test_health_check,
            self.test_user_registration_validation,
            self.test_authentication_flow,
            self.test_health_vault_management,
            self.test_ai_diagnostics_and_hcs10,
            self.test_consent_management,
            self.test_federated_learning,
            self.test_emergency_access,
            self.test_research_participation,
            self.test_error_handling
        ]
        
        total_tests = len(test_methods)
        passed_tests = 0
        
        for test_method in test_methods:
            try:
                result = await test_method()
                if result:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed with error: {e}")
        
        # Print summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("📊 DEMO SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! MediLedger Nexus is working perfectly!")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} tests failed. Check the logs above for details.")
        
        # Save detailed results
        with open("demo_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": total_tests - passed_tests,
                    "success_rate": (passed_tests/total_tests)*100,
                    "duration_seconds": duration,
                    "timestamp": start_time.isoformat()
                },
                "detailed_results": self.demo_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to demo_results.json")


async def main():
    """Main demo function"""
    async with MediLedgerComprehensiveDemo() as demo:
        await demo.run_comprehensive_demo()


if __name__ == "__main__":
    asyncio.run(main())
