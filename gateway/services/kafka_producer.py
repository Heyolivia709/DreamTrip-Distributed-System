"""Kafka 生产者服务 - 发送事件到 Kafka"""
import json
import logging
from typing import Dict, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError

from config import settings


logger = logging.getLogger(__name__)


class KafkaProducerService:
    """Kafka 生产者服务"""
    
    def __init__(self):
        self.producer: Optional[KafkaProducer] = None
        self._initialize_producer()
    
    def _initialize_producer(self):
        """初始化 Kafka 生产者"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[settings.kafka_broker],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # 等待所有副本确认
                retries=3,   # 重试次数
                max_in_flight_requests_per_connection=1,  # 保证消息顺序
                compression_type='gzip'  # 压缩
            )
            logger.info(f"✅ Kafka Producer 已连接: {settings.kafka_broker}")
        except Exception as e:
            logger.warning(f"⚠️  Kafka Producer 初始化失败: {e}")
            logger.warning("系统将在没有 Kafka 的情况下运行")
            self.producer = None
    
    def send_event(
        self, 
        topic: str, 
        event_type: str, 
        data: Dict, 
        key: Optional[str] = None
    ) -> bool:
        """Send 事件到 Kafka
        
        Args:
            topic: Kafka 主题
            event_type: 事件类型
            data: 事件数据
            key: 消息键（用于分区）
            
        Returns:
            Return True if sent successfully，失败返回 False
        """
        if not self.producer:
            logger.warning(f"Kafka Producer 未初始化，跳过发送事件: {event_type}")
            return False
        
        try:
            event = {
                "event_type": event_type,
                "data": data,
                "timestamp": None  # 由 Kafka 自动添加
            }
            
            future = self.producer.send(
                topic=topic,
                value=event,
                key=key
            )
            
            # 异步发送，不阻塞
            future.add_callback(self._on_send_success)
            future.add_errback(self._on_send_error)
            
            logger.info(f"📤 Kafka 事件已发送: {event_type} → {topic}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 发送 Kafka 事件失败: {e}")
            return False
    
    def _on_send_success(self, record_metadata):
        """Send 成功回调"""
        logger.debug(
            f"✅ Kafka 消息已确认: topic={record_metadata.topic}, "
            f"partition={record_metadata.partition}, "
            f"offset={record_metadata.offset}"
        )
    
    def _on_send_error(self, exc):
        """Send 失败回调"""
        logger.error(f"❌ Kafka 消息发送失败: {exc}")
    
    def send_trip_created_event(self, trip_id: int, trip_data: Dict) -> bool:
        """Send 旅行计划创建事件
        
        Args:
            trip_id: Trip plan ID
            trip_data: 旅行计划数据
            
        Returns:
            Return True if sent successfully
        """
        return self.send_event(
            topic="trip_events",
            event_type="trip_created",
            data={
                "trip_id": trip_id,
                "origin": trip_data.get("origin"),
                "destination": trip_data.get("destination"),
                "duration": trip_data.get("duration"),
                "preferences": trip_data.get("preferences")
            },
            key=str(trip_id)
        )
    
    def send_trip_completed_event(self, trip_id: int) -> bool:
        """Send 旅行计划完成事件
        
        Args:
            trip_id: Trip plan ID
            
        Returns:
            Return True if sent successfully
        """
        return self.send_event(
            topic="trip_events",
            event_type="trip_completed",
            data={"trip_id": trip_id},
            key=str(trip_id)
        )
    
    def send_trip_failed_event(self, trip_id: int, error: str) -> bool:
        """Send 旅行计划失败事件
        
        Args:
            trip_id: Trip plan ID
            error: 错误信息
            
        Returns:
            Return True if sent successfully
        """
        return self.send_event(
            topic="trip_events",
            event_type="trip_failed",
            data={
                "trip_id": trip_id,
                "error": error
            },
            key=str(trip_id)
        )
    
    def close(self):
        """关闭生产者"""
        if self.producer:
            self.producer.flush()  # 确保所有消息都发送完成
            self.producer.close()
            logger.info("Kafka Producer 已关闭")


# Singleton
kafka_producer = KafkaProducerService()

