#!/usr/bin/env python3
"""
Kafka consumer example - listen to trip plan events

This script demonstrates how to consume events from the Dream Trip system
Can be used for:
- Real-time monitoring
- Log analysis
- Data synchronization
- Trigger other business processes
"""

import json
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from datetime import datetime


# Configuration logging
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
    """Trip plan event consumer"""
    
    def __init__(self, kafka_broker: str = "localhost:9092"):
        self.consumer = None
        self.kafka_broker = kafka_broker
        self._initialize_consumer()
    
    def _initialize_consumer(self):
        """Initialize Kafka consumer"""
        try:
            self.consumer = KafkaConsumer(
                'trip_events',  # Topic to subscribe to
                bootstrap_servers=[self.kafka_broker],
                group_id='trip_monitor',  # Consumer group
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',  # Start from earliest messages
                enable_auto_commit=True,
                max_poll_records=10
            )
            logger.info(f"{Colors.GREEN}✓ Kafka Consumer connected: {self.kafka_broker}{Colors.END}")
            print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.END}")
            print(f"{Colors.CYAN}{Colors.BOLD}Listening to Kafka event stream...{Colors.END}")
            print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.END}\n")
            
        except KafkaError as e:
            logger.error(f"{Colors.RED}✗ Kafka Consumer initialization failed: {e}{Colors.END}")
            raise
    
    def handle_trip_created(self, event_data: dict):
        """Process trip plan created event"""
        trip_id = event_data.get("trip_id")
        origin = event_data.get("origin")
        destination = event_data.get("destination")
        duration = event_data.get("duration")
        
        print(f"{Colors.GREEN}🆕 Trip plan created{Colors.END}")
        print(f"   Trip ID: {trip_id}")
        print(f"   Route: {origin} → {destination}")
        print(f"   Duration: {duration} days")
        print()
        
        # Additional business logic can be added here:
        # - Send notification to user
        # - Log to data warehouse
        # - Trigger other business processes
    
    def handle_trip_completed(self, event_data: dict):
        """Process trip plan completed event"""
        trip_id = event_data.get("trip_id")
        
        print(f"{Colors.BLUE}✅ Trip plan completed{Colors.END}")
        print(f"   Trip ID: {trip_id}")
        print()
        
        # Additional business logic can be added here:
        # - Send completion notification
        # - Generate statistics report
        # - Update recommendation system
    
    def handle_trip_failed(self, event_data: dict):
        """Process trip plan failed event"""
        trip_id = event_data.get("trip_id")
        error = event_data.get("error")
        
        print(f"{Colors.RED}❌ Trip plan failed{Colors.END}")
        print(f"   Trip ID: {trip_id}")
        print(f"   Error: {error}")
        print()
        
        # Additional business logic can be added here:
        # - Alert notification
        # - Log error details
        # - Trigger retry mechanism
    
    def process_event(self, event: dict):
        """Process event"""
        event_type = event.get("event_type")
        data = event.get("data", {})
        
        # Dispatch processing based on event type
        handlers = {
            "trip_created": self.handle_trip_created,
            "trip_completed": self.handle_trip_completed,
            "trip_failed": self.handle_trip_failed
        }
        
        handler = handlers.get(event_type)
        if handler:
            handler(data)
        else:
            logger.warning(f"Unknown event type: {event_type}")
    
    def start(self):
        """Start consuming events"""
        if not self.consumer:
            logger.error("Consumer not initialized")
            return
        
        try:
            for message in self.consumer:
                # Print message metadata
                print(f"{Colors.YELLOW}[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Partition: {message.partition}, "
                      f"Offset: {message.offset}{Colors.END}")
                
                # Process event
                event = message.value
                self.process_event(event)
                
        except KeyboardInterrupt:
            logger.info(f"\n{Colors.YELLOW}Received interrupt signal, shutting down...{Colors.END}")
        except Exception as e:
            logger.error(f"{Colors.RED}Error occurred while consuming events: {e}{Colors.END}")
        finally:
            self.close()
    
    def close(self):
        """Close consumer"""
        if self.consumer:
            self.consumer.close()
            logger.info(f"{Colors.GREEN}Kafka Consumer closed{Colors.END}")


def main():
    """Main function"""
    print(f"\n{Colors.BOLD}Dream Trip Kafka Event Listener{Colors.END}")
    print(f"{Colors.BOLD}Press Ctrl+C to exit{Colors.END}\n")
    
    try:
        consumer = TripEventConsumer(kafka_broker="localhost:9092")
        consumer.start()
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

