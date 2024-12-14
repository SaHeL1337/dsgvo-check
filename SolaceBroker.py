## Goal: Simple Publisher, event handling and message properties setting
import os
import platform
import time

# Import Solace Python  API modules from the solace package
from solace.messaging.messaging_service import MessagingService, ReconnectionListener, ReconnectionAttemptListener, ServiceInterruptionListener, RetryStrategy, ServiceEvent
from solace.messaging.resources.topic import Topic
from solace.messaging.publisher.persistent_message_publisher import PersistentMessagePublisher
from solace.messaging.publisher.direct_message_publisher import PublishFailureListener, FailedPublishEvent
from solace.messaging.receiver.inbound_message import InboundMessage

class SolaceBroker:

    def __init__(self, host, vpn, username, password):
        self.host = host
        self.vpn = vpn
        self.username = username
        self.password = password
        self.messaging_service = None
        self.direct_publisher = None
        
        if platform.uname().system == 'Windows': os.environ["PYTHONUNBUFFERED"] = "1" # Disable stdout buffer 

        # Broker Config. Note: Could pass other properties Look into
        self.broker_props = {
            "solace.messaging.transport.host": os.environ.get('SOLACE_HOST') or host,
            "solace.messaging.service.vpn-name": os.environ.get('SOLACE_VPN') or vpn,
            "solace.messaging.authentication.scheme.basic.username": os.environ.get('SOLACE_USERNAME') or username,
            "solace.messaging.authentication.scheme.basic.password": os.environ.get('SOLACE_PASSWORD') or password
            }
        
        # Build A messaging service with a reconnection strategy of 20 retries over an interval of 3 seconds
        self.messaging_service = MessagingService.builder().from_properties(self.broker_props)\
                    .with_reconnection_retry_strategy(RetryStrategy.parametrized_retry(20,3))\
                    .build()
        
        # Blocking connect thread
        self.messaging_service.connect()
        print(f'Messaging Service connected? {self.messaging_service.is_connected}')

        # Event Handling for the messaging service
        service_handler = self.ServiceEventHandler()
        self.messaging_service.add_reconnection_listener(service_handler)
        self.messaging_service.add_reconnection_attempt_listener(service_handler)
        self.messaging_service.add_service_interruption_listener(service_handler)

        # Create a direct message publisher and start it
        self.publisher: PersistentMessagePublisher = self.messaging_service.create_persistent_message_publisher_builder().build()
        

        # Blocking Start thread
        self.publisher.start()
        print(f'Direct Publisher ready? {self.publisher.is_ready()}')

        

    # Inner classes for error handling
    class ServiceEventHandler(ReconnectionListener, ReconnectionAttemptListener, ServiceInterruptionListener):
        def on_reconnected(self, e: ServiceEvent):
            print("\non_reconnected")
            print(f"Error cause: {e.get_cause()}")
            print(f"Message: {e.get_message()}")
        
        def on_reconnecting(self, e: "ServiceEvent"):
            print("\non_reconnecting")
            print(f"Error cause: {e.get_cause()}")
            print(f"Message: {e.get_message()}")

        def on_service_interrupted(self, e: "ServiceEvent"):
            print("\non_service_interrupted")
            print(f"Error cause: {e.get_cause()}")
            print(f"Message: {e.get_message()}")
 
    class PublisherErrorHandling(PublishFailureListener):
        def on_failed_publish(self, e: "FailedPublishEvent"):
            print("on_failed_publish")

    


    def publish(self, message_body, publish_topic):
        # Prepare outbound message payload and body
        outbound_msg_builder = self.messaging_service.message_builder() \
                        .with_application_message_id("sample_id") \
                        .with_property("application", "samples") \
                        .with_property("language", "Python") \

        topic = Topic.of(publish_topic)
         # Direct publish the message with dynamic headers and payload
        outbound_msg = outbound_msg_builder \
                        .with_application_message_id(f'NEW 1')\
                        .build(message_body)
        self.publisher.publish(destination=topic, message=outbound_msg)

        print(f'Published message on {topic}')


    def __destroy__(self):
        # Terminate the direct publisher
        self.publisher.terminate()
        # Disconnect the messaging service
        self.messaging_service.disconnect()


