from curses.ascii import SO
from SolaceBroker import SolaceBroker
from Webcrawler import Webcrawler
from database import db_session
from Models.Result import Result
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.receiver.message_receiver import MessageHandler
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.receiver.persistent_message_receiver import PersistentMessageReceiver
from solace.messaging.resources.queue import Queue
from solace.messaging.config.missing_resources_creation_configuration import MissingResourcesCreationStrategy
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
SOLACE_HOST = config['SOLACE']['HOST']
SOLACE_VPN = config['SOLACE']['VPN']
SOLACE_USERNAME = config['SOLACE']['USERNAME']
SOLACE_PASSWORD = config['SOLACE']['PASSWORD']

# Handle received messages
class MessageHandlerImpl(MessageHandler):
    def __init__(self, persistent_receiver: PersistentMessageReceiver):
        self.receiver: PersistentMessageReceiver = persistent_receiver

    def on_message(self, message: 'InboundMessage'):
        # Check if the payload is a String or Byte, decode if its the later
        baseUrl = message.get_payload_as_string() if message.get_payload_as_string() != None else message.get_payload_as_bytes()
        if isinstance(baseUrl, bytearray):
            print(f"Received a message of type: {type(baseUrl)}. Decoding to string")
            baseUrl = baseUrl.decode()

        topic = message.get_destination_name()
        print("\n" + f"Received message on: {topic}")
        print("\n" + f"Message payload: {baseUrl} \n")

        crawler = Webcrawler(baseUrl, 2)
        crawler.crawl()
        
        for url in crawler.externalResources:
            for resource in crawler.externalResources[url]:
                r = Result(baseUrl,url,str(resource))
                db_session.add(r)
                db_session.commit()

        self.receiver.ack(message)
        


print("Server started")

broker = SolaceBroker(SOLACE_HOST,SOLACE_VPN,SOLACE_USERNAME,SOLACE_PASSWORD)

queue_name = "q/crawl2"
durable_exclusive_queue = Queue.durable_exclusive_queue(queue_name)

try:
    persistent_receiver: PersistentMessageReceiver = broker.messaging_service.create_persistent_message_receiver_builder()\
                .with_missing_resources_creation_strategy(MissingResourcesCreationStrategy.DO_NOT_CREATE)\
                .build(durable_exclusive_queue)
    persistent_receiver.start()
    persistent_receiver.add_subscription(TopicSubscription.of("t/crawl"))
except PubSubPlusClientError as e:
    print(f"Make sure queue exists on broker: {e}")

# Callback for received messages
persistent_receiver.receive_async(MessageHandlerImpl(persistent_receiver))

print(f'Direct Receiver ready? {persistent_receiver.is_running()}')