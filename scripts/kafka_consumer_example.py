#!/usr/bin/env python3
"""
Kafka 消费者示例 - 监听旅行计划事件

这个脚本展示如何消费来自 Dream Trip 系统的事件
可以用于：
- 实时监控
- 日志分析
- 数据同步
- 触发其他业务流程
"""

import json
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from datetime import datetime


# Configuration日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Colors:
    """Terminal colors"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    END = '\033[0m'


class TripEventConsumer:
    """旅行计划事件消费者"""
    
    def __init__(self, kafka_broker: str = "localhost:9092"):
        self.consumer = None
        self.kafka_broker = kafka_broker
        self._initialize_consumer()
    
    def _initialize_consumer(self):
        """初始化 Kafka 消费者"""
        try:
            self.consumer = KafkaConsumer(
                'trip_events',  # 订阅的主题
                bootstrap_servers=[self.kafka_broker],
                group_id='trip_monitor',  # 消费者组
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',  # 从最早的消息开始
                enable_auto_commit=True,
                max_poll_records=10
            )
            logger.info(f"{Colors.GREEN}✓ Kafka Consumer 已连接: {self.kafka_broker}{Colors.END}")
            print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.END}")
            print(f"{Colors.CYAN}{Colors.BOLD}监听 Kafka 事件流...{Colors.END}")
            print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.END}\n")
            
        except KafkaError as e:
            logger.error(f"{Colors.RED}✗ Kafka Consumer 初始化失败: {e}{Colors.END}")
            raise
    
    def handle_trip_created(self, event_data: dict):
        """Process 旅行计划创建事件"""
        trip_id = event_data.get("trip_id")
        origin = event_data.get("origin")
        destination = event_data.get("destination")
        duration = event_data.get("duration")
        
        print(f"{Colors.GREEN}🆕 旅行计划已创建{Colors.END}")
        print(f"   Trip ID: {trip_id}")
        print(f"   路线: {origin} → {destination}")
        print(f"    days数: {duration}")
        print()
        
        # Additional business logic can be added here:
        # - 发送通知给用户
        # - 记录到数据仓库
        # - 触发其他业务流程
    
    def handle_trip_completed(self, event_data: dict):
        """Process 旅行计划完成事件"""
        trip_id = event_data.get("trip_id")
        
        print(f"{Colors.BLUE}✅ 旅行计划已完成{Colors.END}")
        print(f"   Trip ID: {trip_id}")
        print()
        
        # Additional business logic can be added here:
        # - 发送完成通知
        # - 生成统计报告
        # - 更新推荐系统
    
    def handle_trip_failed(self, event_data: dict):
        """Process 旅行计划失败事件"""
        trip_id = event_data.get("trip_id")
        error = event_data.get("error")
        
        print(f"{Colors.RED}❌ 旅行计划失败{Colors.END}")
        print(f"   Trip ID: {trip_id}")
        print(f"   错误: {error}")
        print()
        
        # Additional business logic can be added here:
        # - 告警通知
        # - 记录错误日志
        # - 触发重试机制
    
    def process_event(self, event: dict):
        """Process 事件"""
        event_type = event.get("event_type")
        data = event.get("data", {})
        
        # 根据事件类型分发处理
        handlers = {
            "trip_created": self.handle_trip_created,
            "trip_completed": self.handle_trip_completed,
            "trip_failed": self.handle_trip_failed
        }
        
        handler = handlers.get(event_type)
        if handler:
            handler(data)
        else:
            logger.warning(f"未知事件类型: {event_type}")
    
    def start(self):
        """开始消费事件"""
        if not self.consumer:
            logger.error("Consumer 未初始化")
            return
        
        try:
            for message in self.consumer:
                # 打印消息元数据
                print(f"{Colors.YELLOW}[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Partition: {message.partition}, "
                      f"Offset: {message.offset}{Colors.END}")
                
                # 处理事件
                event = message.value
                self.process_event(event)
                
        except KeyboardInterrupt:
            logger.info(f"\n{Colors.YELLOW}收到中断信号，正在关闭...{Colors.END}")
        except Exception as e:
            logger.error(f"{Colors.RED}消费事件时发生错误: {e}{Colors.END}")
        finally:
            self.close()
    
    def close(self):
        """关闭消费者"""
        if self.consumer:
            self.consumer.close()
            logger.info(f"{Colors.GREEN}Kafka Consumer 已关闭{Colors.END}")


def main():
    """主函数"""
    print(f"\n{Colors.BOLD}Dream Trip Kafka 事件监听器{Colors.END}")
    print(f"{Colors.BOLD}按 Ctrl+C 退出{Colors.END}\n")
    
    try:
        consumer = TripEventConsumer(kafka_broker="localhost:9092")
        consumer.start()
    except Exception as e:
        logger.error(f"启动失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

