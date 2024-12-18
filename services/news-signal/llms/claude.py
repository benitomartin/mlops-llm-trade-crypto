import json
from typing import Literal, Optional

from llama_index.core.prompts import PromptTemplate
from llama_index.llms.anthropic import Anthropic
from llms.base import BaseNewsSignalExtractor, NewsSignal  #,  NewsSignalOneCoin


class ClaudeNewsSignalExtractor(BaseNewsSignalExtractor):
    def __init__(
        self,
        llm_name: str,
        api_key: str,
        temperature: Optional[float] = 0,
    ):
        self.llm = Anthropic(
            model=llm_name,
            api_key=api_key,
            temperature=temperature,
        )

        self.prompt_template = PromptTemplate(
            template="""
            You are an expert crypto financial analyst with deep knowledge of market dynamics and sentiment analysis.
            Analyze the following news story and determine its potential impact on crypto asset prices.
            Focus on both direct mentions and indirect implications for each asset.

            Do not output data for a given coin if the news is not relevant to it.

            ## Example input
            "Goldman Sachs wants to invest in Bitcoin and Ethereum, but not in XRP"

            ## Example output
            [
                {"coin": "BTC", "signal": 1},
                {"coin": "ETH", "signal": 1},
                {"coin": "XRP", "signal": -1},
            ]

            News article: {news_article}

            OUTPUT ONLY THE JSON. NO ADDITIONAL TEXT.
            """
        )

        self.llm_name = llm_name

    # Update the method in the extractor class
    def get_signal(
        self,
        text: str,
        output_format: Literal['dict', 'NewsSignal'] = 'NewsSignal',
    ) -> NewsSignal | dict | None:
        try:
            # Use chat completion and parse the JSON manually
            response = self.llm.complete(
                self.prompt_template.format(news_article=text)
            )

            # Parse the JSON response
            parsed_response = json.loads(response.text)

            # Create NewsSignal with the full parsed response
            news_signal = NewsSignal(news_signals=parsed_response)

            # # If no valid signals, return None
            # if not news_signal.news_signals:
            #     pass

            if output_format == 'dict':
                return news_signal.model_dump()['news_signals']
            else:
                return news_signal

        except Exception as e:
            print(f'Error occurred during request: {e}')
            raise


if __name__ == '__main__':
    from config import AnthropicConfig

    config = AnthropicConfig()

    llm = ClaudeNewsSignalExtractor(
        llm_name=config.llm_name,
        api_key=config.api_key,
    )

    examples = [
        'Bitcoin BTC ads spotted on China’s Alipay payment app',
        'U.S. Supreme Court Lets Nvidia’s Crypto Lawsuit Move Forward',
        'Trump’s World Liberty Acquires ETH, LINK, and AAVE in $12M Crypto Shopping Spree',
    ]

    for example in examples:
        print(f'Example: {example}')
        response = llm.get_signal(example)
        print(response)






    # """
    # Example: Bitcoin ETF ads spotted on China’s Alipay payment app
    # {
    #     "btc_signal": 1,
    #     "eth_signal": 0,
    #     "reasoning": "The news of Bitcoin ETF ads being spotted on China's Alipay payment
    #     app suggests a growing interest in Bitcoin and other cryptocurrencies among Chinese
    #     investors. This could lead to increased demand for BTC, causing its price to rise."
    # }

    # Example: U.S. Supreme Court Lets Nvidia’s Crypto Lawsuit Move Forward
    # {
    #     "btc_signal": -1,
    #     "eth_signal": -1,
    #     "reasoning": "The US Supreme Court's decision allows Nvidia to pursue its crypto
    #     lawsuit, which could lead to increased regulatory uncertainty and potential
    #     restrictions on cryptocurrency mining. This could negatively impact the prices
    #     of both BTC and ETH."
    # }

    # Example: Trump’s World Liberty Acquires ETH, LINK, and AAVE in $12M Crypto Shopping Spree
    # {
    #     "btc_signal": 0,
    #     "eth_signal": 1,
    #     "reasoning": "The acquisition of ETH by a major company like
    #     Trump's World Liberty suggests that there is increased demand for
    #     Ethereum, which could lead to an increase in its price."
    # }
    # """


    # def get_signal(
    #     self,
    #     text: str,
    #     output_format: Literal['dict', 'NewsSignal'] = 'NewsSignal',
    # ) -> NewsSignal | dict:
    #     """
    #     Get the news signal from the given `text`

    #     Args:
    #         text: The news article to get the signal from
    #         output_format: The format of the output

    #     Returns:
    #         The news signal
    #     """
    #     try:
    #         # Use chat completion and parse the JSON manually
    #         response = self.llm.complete(self.prompt_template.format(news_article=text))

    #         # Parse the JSON response
    #         parsed_response = self.extract_json(response.text)

    #         # Get the allowed coins from the NewsSignalOneCoin model
    #         allowed_coins = NewsSignalOneCoin.model_fields['coin'].annotation.__args__

    #         # Convert to NewsSignal by creating a list of NewsSignalOneCoin
    #         # Only include signals that are 1 or -1 and have supported coins
    #         news_signals = [
    #             NewsSignalOneCoin(coin=signal['coin'], signal=signal['signal'])
    #             for signal in parsed_response
    #             if signal['signal'] in [1, -1] and signal['coin'] in allowed_coins
    #         ]
    #         # breakpoint()
    #         # Only create NewsSignal if there are relevant signals
    #         if news_signals:
    #             news_signal = NewsSignal(news_signals=news_signals)

    #             if output_format == 'dict':
    #                 return news_signal.model_dump()
    #             else:
    #                 return news_signal
    #         else:
    #             # If no relevant signals, return None or raise an exception
    #             return None
    #     except Exception as e:
    #         print(f'Error occurred during request: {e}')
    #         raise
