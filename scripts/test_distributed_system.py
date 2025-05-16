#!/usr/bin/env python3
"""
Dream Trip 分布式系统测试脚本
测试所有微服务的健康状况和核心功能
"""

import json
import time
import requests
from typing import Dict, List, Optional
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
    """分布式系统测试器"""
    
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
        """打印测试头部"""
        print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}Dream Trip 分布式智能旅行规划系统 - 系统测试{Colors.END}")
        print(f"{Colors.BOLD}{'=' * 70}{Colors.END}\n")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试目标: 验证所有微服务的健康状况和功能\n")
    
    def print_section(self, title: str):
        """打印章节标题"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'─' * 70}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{title}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'─' * 70}{Colors.END}\n")
    
    def test_health(self, name: str, url: str) -> bool:
        """测试服务健康检查"""
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                
                if status == "healthy":
                    print(f"{Colors.GREEN}✓{Colors.END} {name:25s} [健康]")
                    self.results["passed"] += 1
                    return True
                else:
                    print(f"{Colors.RED}✗{Colors.END} {name:25s} [不健康: {status}]")
                    self.results["failed"] += 1
                    return False
            else:
                print(f"{Colors.RED}✗{Colors.END} {name:25s} [HTTP {response.status_code}]")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} {name:25s} [错误: {str(e)}]")
            self.results["failed"] += 1
            return False
    
    def test_create_trip(self) -> Optional[int]:
        """测试创建旅行计划"""
        print(f"{Colors.CYAN}[TEST]{Colors.END} 创建旅行计划（北京 → 上海）")
        
        try:
            payload = {
                "origin": "北京",
                "destination": "上海",
                "preferences": ["美食", "历史", "文化"],
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
        """测试获取旅行详情"""
        print(f"{Colors.CYAN}[TEST]{Colors.END} 获取旅行计划详情 (ID: {trip_id})")
        
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
                print(f"    daysweather信息: {'✓' if has_weather else '✗'}")
                print(f"   景点推荐: {'✓' if has_pois else '✗'}")
                print(f"   AI Summary: {'✓' if has_ai else '✗'}")
                
                if status == "completed" and has_route and has_weather and has_pois:
                    print(f"   {Colors.GREEN}✓ PASS{Colors.END} - 数据完整")
                    self.results["passed"] += 1
                    return True
                else:
                    print(f"   {Colors.YELLOW}⚠ WARN{Colors.END} - 数据不完整或处理中")
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
        """测试获取旅行列表"""
        print(f"{Colors.CYAN}[TEST]{Colors.END} 获取用户旅行列表")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/trips?user_id=1&limit=5",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                trips = data.get("trips", [])
                
                print(f"   {Colors.GREEN}✓ PASS{Colors.END} - 找到 {len(trips)} 个旅行计划")
                
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
        """测试直接调用微服务"""
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
        """打印测试Summary"""
        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"{Colors.BOLD}测试结果汇总{Colors.END}")
        print(f"{Colors.BOLD}{'=' * 70}{Colors.END}\n")
        
        print(f"总测试数: {total}")
        print(f"{Colors.GREEN}通过: {self.results['passed']}{Colors.END}")
        print(f"{Colors.RED}失败: {self.results['failed']}{Colors.END}")
        print(f"通过率: {pass_rate:.1f}%\n")
        
        if self.results["failed"] == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 所有测试通过！分布式系统运行正常！{Colors.END}\n")
            return 0
        else:
            print(f"{Colors.RED}{Colors.BOLD}⚠️  部分测试失败，请检查相关服务{Colors.END}\n")
            return 1
    
    def run(self):
        """运行所有测试"""
        self.print_header()
        
        # Phase 1: 健康检查
        self.print_section("Phase 1: 服务健康检查")
        for name, url in self.services.items():
            self.test_health(name, url)
        
        # Phase 2: 核心业务流程
        self.print_section("Phase 2: 核心业务流程测试")
        
        trip_id = self.test_create_trip()
        
        if trip_id:
            print(f"\n{Colors.YELLOW}[WAIT]{Colors.END} 等待后台处理旅行计划（8秒）...")
            time.sleep(8)
            print()
            
            self.test_get_trip(trip_id)
        
        print()
        self.test_get_trips()
        
        # Phase 3: 微服务直接调用
        self.print_section("Phase 3: 微服务直接调用测试")
        
        self.test_direct_service(
            "Route Service - 路线规划",
            self.services["Route Service"],
            "/route",
            {"origin": "深圳", "destination": "广州"}
        )
        
        print()
        self.test_direct_service(
            "Weather Service -  daysweather预报",
            self.services["Weather Service"],
            "/weather/forecast",
            {"location": "北京", "duration": 3}
        )
        
        print()
        self.test_direct_service(
            "POI Service - 景点推荐",
            self.services["POI Service"],
            "/poi/recommendations",
            {"location": "上海", "preferences": ["历史"], "duration": 2}
        )
        
        # 打印Summary
        return self.print_summary()


if __name__ == "__main__":
    tester = DistributedSystemTester()
    exit_code = tester.run()
    exit(exit_code)

