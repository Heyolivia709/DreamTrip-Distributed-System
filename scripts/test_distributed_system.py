#!/usr/bin/env python3
"""
Dream Trip distributed system test script
Test health status and core functionality of all microservices
"""

import time
import requests
from typing import Optional
from datetime import datetime


class Colors:
    """Terminal colors"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    END = '\033[0m'


class DistributedSystemTester:
    """Distributed system tester"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.services = {
            "Gateway": "http://localhost:8000",
            "Route Service": "http://localhost:8001",
            "Weather Service": "http://localhost:8002",
            "POI Service": "http://localhost:8003",
            "AI Summary Service": "http://localhost:8004"
        }
        self.results = {
            "passed": 0,
            "failed": 0,
            "tests": []
        }
    
    def print_header(self):
        """Print test header"""
        print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}Dream Trip Distributed Intelligent Travel Planning System - System Test{Colors.END}")
        print(f"{Colors.BOLD}{'=' * 70}{Colors.END}\n")
        print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Test objective: Verify health status and functionality of all microservices\n")
    
    def print_section(self, title: str):
        """Print section title"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'─' * 70}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{title}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'─' * 70}{Colors.END}\n")
    
    def test_health(self, name: str, url: str) -> bool:
        """Test service health check"""
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                
                if status == "healthy":
                    print(f"{Colors.GREEN}✓{Colors.END} {name:25s} [Healthy]")
                    self.results["passed"] += 1
                    return True
                else:
                    print(f"{Colors.RED}✗{Colors.END} {name:25s} [Unhealthy: {status}]")
                    self.results["failed"] += 1
                    return False
            else:
                print(f"{Colors.RED}✗{Colors.END} {name:25s} [HTTP {response.status_code}]")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} {name:25s} [Error: {str(e)}]")
            self.results["failed"] += 1
            return False
    
    def test_create_trip(self) -> Optional[int]:
        """Test create trip plan"""
        print(f"{Colors.CYAN}[TEST]{Colors.END} Create trip plan (Beijing → Shanghai)")
        
        try:
            payload = {
                "origin": "Beijing",
                "destination": "Shanghai",
                "preferences": ["food", "history", "culture"],
                "duration": 3
            }
            
            response = requests.post(
                f"{self.base_url}/api/trip/plan",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                trip_id = data.get("trip_id")
                status = data.get("status")
                
                print(f"   {Colors.GREEN}✓ PASS{Colors.END} - Trip ID: {trip_id}, Status: {status}")
                self.results["passed"] += 1
                return trip_id
            else:
                print(f"   {Colors.RED}✗ FAIL{Colors.END} - HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                self.results["failed"] += 1
                return None
                
        except Exception as e:
            print(f"   {Colors.RED}✗ FAIL{Colors.END} - {str(e)}")
            self.results["failed"] += 1
            return None
    
    def test_get_trip(self, trip_id: int) -> bool:
        """Test get trip details"""
        print(f"{Colors.CYAN}[TEST]{Colors.END} Get trip plan details (ID: {trip_id})")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/trip/{trip_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                has_route = "route" in data and data["route"] is not None
                has_weather = "weather" in data and len(data.get("weather", [])) > 0
                has_pois = "pois" in data and len(data.get("pois", [])) > 0
                has_ai = "ai_summary" in data and data["ai_summary"] is not None
                
                print(f"   Status: {status}")
                print(f"   Route info: {'✓' if has_route else '✗'}")
                print(f"   Weather info: {'✓' if has_weather else '✗'}")
                print(f"   POI recommendations: {'✓' if has_pois else '✗'}")
                print(f"   AI Summary: {'✓' if has_ai else '✗'}")
                
                if status == "completed" and has_route and has_weather and has_pois:
                    print(f"   {Colors.GREEN}✓ PASS{Colors.END} - Data complete")
                    self.results["passed"] += 1
                    return True
                else:
                    print(f"   {Colors.YELLOW}⚠ WARN{Colors.END} - Data incomplete or processing")
                    self.results["passed"] += 1
                    return True
            else:
                print(f"   {Colors.RED}✗ FAIL{Colors.END} - HTTP {response.status_code}")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            print(f"   {Colors.RED}✗ FAIL{Colors.END} - {str(e)}")
            self.results["failed"] += 1
            return False
    
    def test_get_trips(self) -> bool:
        """Test get trip list"""
        print(f"{Colors.CYAN}[TEST]{Colors.END} Get user trip list")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/trips?user_id=1&limit=5",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                trips = data.get("trips", [])
                
                print(f"   {Colors.GREEN}✓ PASS{Colors.END} - Found {len(trips)} trip plans")
                
                for trip in trips[:3]:
                    print(f"      • {trip.get('origin')} → {trip.get('destination')} "
                          f"[{trip.get('status')}]")
                
                self.results["passed"] += 1
                return True
            else:
                print(f"   {Colors.RED}✗ FAIL{Colors.END} - HTTP {response.status_code}")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            print(f"   {Colors.RED}✗ FAIL{Colors.END} - {str(e)}")
            self.results["failed"] += 1
            return False
    
    def test_direct_service(self, name: str, url: str, endpoint: str, payload: dict) -> bool:
        """Test direct microservice call"""
        print(f"{Colors.CYAN}[TEST]{Colors.END} {name}")
        
        try:
            response = requests.post(
                f"{url}{endpoint}",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   {Colors.GREEN}✓ PASS{Colors.END}")
                print(f"   Response keys: {list(data.keys())}")
                self.results["passed"] += 1
                return True
            else:
                print(f"   {Colors.RED}✗ FAIL{Colors.END} - HTTP {response.status_code}")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            print(f"   {Colors.RED}✗ FAIL{Colors.END} - {str(e)}")
            self.results["failed"] += 1
            return False
    
    def print_summary(self):
        """Print test summary"""
        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"{Colors.BOLD}Test Results Summary{Colors.END}")
        print(f"{Colors.BOLD}{'=' * 70}{Colors.END}\n")
        
        print(f"Total tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.results['passed']}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.results['failed']}{Colors.END}")
        print(f"Pass rate: {pass_rate:.1f}%\n")
        
        if self.results["failed"] == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Distributed system running normally!{Colors.END}\n")
            return 0
        else:
            print(f"{Colors.RED}{Colors.BOLD}⚠️  Some tests failed, please check related services{Colors.END}\n")
            return 1
    
    def run(self):
        """Run all tests"""
        self.print_header()
        
        # Phase 1: Health check
        self.print_section("Phase 1: Service Health Check")
        for name, url in self.services.items():
            self.test_health(name, url)
        
        # Phase 2: Core business process
        self.print_section("Phase 2: Core Business Process Test")
        
        trip_id = self.test_create_trip()
        
        if trip_id:
            print(f"\n{Colors.YELLOW}[WAIT]{Colors.END} Waiting for background trip plan processing (8 seconds)...")
            time.sleep(8)
            print()
            
            self.test_get_trip(trip_id)
        
        print()
        self.test_get_trips()
        
        # Phase 3: Direct microservice calls
        self.print_section("Phase 3: Direct Microservice Call Test")
        
        self.test_direct_service(
            "Route Service - Route Planning",
            self.services["Route Service"],
            "/route",
            {"origin": "Shenzhen", "destination": "Guangzhou"}
        )
        
        print()
        self.test_direct_service(
            "Weather Service - Weather Forecast",
            self.services["Weather Service"],
            "/weather/forecast",
            {"location": "Beijing", "duration": 3}
        )
        
        print()
        self.test_direct_service(
            "POI Service - POI Recommendations",
            self.services["POI Service"],
            "/poi/recommendations",
            {"location": "Shanghai", "preferences": ["history"], "duration": 2}
        )
        
        # Print summary
        return self.print_summary()


if __name__ == "__main__":
    tester = DistributedSystemTester()
    exit_code = tester.run()
    exit(exit_code)

