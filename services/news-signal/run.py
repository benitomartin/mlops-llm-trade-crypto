from llms.base import BaseNewsSignalExtractor
from loguru import logger
from quixstreams import Application
from typing import List, Optional


def add_signal_to_news(value: dict) -> dict:
    """
    From the given news in value['title'] extract the news signal using the LLM.
    """
    logger.debug(f'Extracting news signal from {value["title"]}')
    news_signal: List[dict] = llm.get_signal(value['title'], output_format='list')

    # If the news_signal list is empty, ignore and return an empty list
    if not news_signal:
        logger.debug('News signal is empty, skipping processing.')
        return []
    
    model_name = llm.llm_name
    timestamp_ms = value['timestamp_ms']
    
    # breakpoint()

    try:
        output = [
            {
                'coin': n['coin'],
                'signal': n['signal'],
                'model_name': model_name,
                'timestamp_ms': timestamp_ms,
            }
            for n in news_signal 
        ]
    except Exception as e:
        logger.error(f'Cannot extract news signal from {news_signal}')
        logger.error(f'Error extracting news signal: {e}')
        return []

    return output


def main(
    kafka_broker_address: str,
    kafka_input_topic: str,
    kafka_output_topic: str,
    kafka_consumer_group: str,
    llm: BaseNewsSignalExtractor,
    debug: Optional[bool] = False,

):
    logger.info('Hello from news-signal!')

    if debug:
        # just a hack to make the consumer group unique so we make sure that while
        # debugging we get a message quickly
        import time

        unique_id = str(int(time.time() * 1000))
        kafka_consumer_group = f'{kafka_consumer_group}-{unique_id}'

    app = Application(
        broker_address=kafka_broker_address,
        consumer_group=kafka_consumer_group,
        auto_offset_reset='earliest',
    )

    input_topic = app.topic(
        name=kafka_input_topic,
        value_deserializer='json',
    )

    output_topic = app.topic(
        name=kafka_output_topic,
        value_serializer='json',
    )

    sdf = app.dataframe(input_topic)

    sdf = sdf.apply(add_signal_to_news, expand=True)
    
    # # Process the incoming news into a news signal
    # sdf = sdf.apply(
    #     lambda value: {
    #         'news': value['title'],
    #         **llm.get_signal(value['title']),
    #         'model_name': llm.llm_name,
    #         'timestamp_ms': value['timestamp_ms'],
    #     }
    # )

    sdf = sdf.update(lambda value: logger.debug(f'Final message: {value}'))

    sdf = sdf.to_topic(output_topic)

    app.run()


if __name__ == '__main__':
    from config import config
    from llms.factory import get_llm

    logger.info(f'Using model provider: {config.model}')
    llm = get_llm(config.model)

    main(
        kafka_broker_address=config.kafka_broker_address,
        kafka_input_topic=config.kafka_input_topic,
        kafka_output_topic=config.kafka_output_topic,
        kafka_consumer_group=config.kafka_consumer_group,
        llm=llm,
    )
