import os
import time
import boto3
from boto3.dynamodb.types import TypeDeserializer
from kombu import Connection, Exchange, Queue, Message, Producer
from mlsgpt import core, store, logger, models


mls_exchange = Exchange("mls", type="direct", durable=True)
file_queue = Queue(
    "mls.process-file", exchange=mls_exchange, routing_key="process-file"
)
page_queue = Queue(
    "mls.process-page", exchange=mls_exchange, routing_key="process-page"
)


def create_rabbitmq_connection():
    return Connection(
        f"amqp://{os.environ.get('RABBITMQ_USER')}:{os.environ.get('RABBITMQ_PASSWORD')}@{os.environ.get('RABBITMQ_HOST')}:{os.environ.get('RABBITMQ_PORT')}/%2F"
    )


def get_stream_arn():
    dynamodb = boto3.client("dynamodb")
    ssm = boto3.client("ssm")
    parameter_name = os.environ["DOCAI_RESULTS_TABLE"]
    table_name = ssm.get_parameter(Name=parameter_name)["Parameter"]["Value"]
    table = dynamodb.describe_table(TableName=table_name)
    return table["Table"]["LatestStreamArn"]


def process_file(log: logger.logging.Logger, pub: Producer):
    def _(body: str, message: Message):
        file = models.FileInfo(**body)
        log.info(f"Message id: {file.id} received")

        images, mime_type = core.prepare_request(file.download_link, file.mime_type)
        size = len(images)
        log.info(f"Message id: {file.id} split into {size} pages")

        for i, image in enumerate(images):
            page = models.Page(
                id=file.id, num=i + 1, content=image, mime_type=mime_type
            )
            pub.publish(
                page.model_dump(),
                exchange=mls_exchange,
                routing_key="process-page",
                declare=[page_queue],
            )

            log.info(f"Message id: {file.id} {page.num}/{size} published")

        message.ack()

    return _


def process_page(log: logger.logging.Logger):
    def _(body: str, message: Message):
        page = models.Page(**body)
        log.info(f"Message id: {page.id} page: {page.num} received")
        ret = core.extract_data(page.content, page.mime_type)
        log.info(
            f"Extraction id: {page.id} page: {page.num} queued, request_id: {ret['result']['request_id'][:8]}..."
        )
        message.ack()

    return _


def split_pages():
    log = logger.get_logger("split-pages")
    with create_rabbitmq_connection() as conn:
        pub = conn.Producer(serializer="json")
        log.info("RabbitMQ connection established")
        with conn.Consumer(file_queue, callbacks=[process_file(log, pub)]) as _:
            log.info("File queue consumer started")
            while True:
                conn.drain_events()


def extract_data():
    log = logger.get_logger("extract-data")
    with create_rabbitmq_connection() as conn:
        log.info("RabbitMQ connection established")
        with conn.Consumer(page_queue, callbacks=[process_page(log)]) as _:
            log.info("Page queue consumer started")
            while True:
                conn.drain_events()


def deserialize_dynamodb_json(node):
    """Convert DynamoDB item to Python dictionary."""
    deserializer = TypeDeserializer()
    if isinstance(node, list):
        return [deserialize_dynamodb_json(item) for item in node]
    elif isinstance(node, dict):
        return {key: deserializer.deserialize(value) for key, value in node.items()}
    else:
        return node  # In case the input is already deserialized


def process_record(
    record: dict,
    schema_name: str,
    schema_version: str,
    writer: store.DataWriter,
    log: logger.logging.Logger,
):
    if record["eventName"] == "INSERT":
        new_image = record["dynamodb"]["NewImage"]
        item = deserialize_dynamodb_json(new_image)

        if (
            item["schema_name"] == schema_name
            and item["schema_version"] == schema_version
        ):

            error = item.get("error")
            result = item.get("result")
            request_id = item["request_id"]
            log.info(f"Results for request_id:{request_id[:8]}... received")

            if error:
                log.error(
                    f"Results for request_id: {request_id[:8]}... failed error: {error}"
                )
                return

            if result:
                writer.save(dict(request_id=request_id, data=result))
                log.info(f"Results for request_id:{request_id[:8]}... saved")
                return request_id


def save_results():
    log = logger.get_logger("save-results")
    stream_arn = get_stream_arn()
    client = boto3.client("dynamodbstreams")
    shard_id = client.describe_stream(StreamArn=stream_arn)["StreamDescription"][
        "Shards"
    ][0]["ShardId"]
    shard_iterator = client.get_shard_iterator(
        StreamArn=stream_arn, ShardId=shard_id, ShardIteratorType="LATEST"
    )["ShardIterator"]
    log.info("DynamoDB stream connection established")
    log.info("Shard iterator obtained")

    writer = store.DataWriter(log=log)
    log.info("Results datastore started")

    schema_name = os.environ.get("DOCAI_SCHEMA_NAME")
    schema_version = os.environ.get("DOCAI_SCHEMA_VERSION")

    while True:
        out = client.get_records(ShardIterator=shard_iterator)
        records = out["Records"]

        if records:
            for record in records:
                process_record(record, schema_name, schema_version, writer, log)

        shard_iterator = out["NextShardIterator"]
        time.sleep(5)
