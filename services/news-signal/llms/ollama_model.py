import json
import re
from typing import Literal, Optional

from .base import BaseNewsSignalExtractor, NewsSignal
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.ollama import Ollama


class OllamaNewsSignalExtractor(BaseNewsSignalExtractor):
    def __init__(
        self,
        llm_name: str,
        temperature: Optional[float] = 0,
    ):
        self.llm = Ollama(
            model=llm_name,
            # base_url= "http://localhost:11434",
            temperature=temperature,
        )


        self.prompt_template = PromptTemplate(
            template="""
            You are a financial analyst.
            You are given a news article and you need to determine the impact of the news on the BTC and ETH price.

            Respond STRICTLY with a JSON in this EXACT format:
            {
                "btc_signal": 1,
                "eth_signal": 0,
                "reasoning": "Explanation of the signals"
            }

            Rules for signals:
            - 1 means price is expected to go up
            - 0 means price is expected to stay the same
            - -1 means price is expected to go down

            News article: {news_article}

            OUTPUT ONLY THE JSON. NO ADDITIONAL TEXT.
            """
        )

        self.llm_name = llm_name

    # def extract_json(self, text: str) -> dict:
    #     """
    #     Extract JSON from the response text using multiple methods
    #     """
    #     # Method 1: Find JSON between first { and last }
    #     try:
    #         first_brace = text.index('{')
    #         last_brace = text.rindex('}')
    #         json_str = text[first_brace:last_brace+1]
    #         return json.loads(json_str)
    #     except (ValueError, json.JSONDecodeError):
    #         pass

    #     raise ValueError(f"Could not extract valid JSON from text: {text}")


    def extract_json(self, response_text: str) -> NewsSignal:
        try:
            # Parse and validate using Pydantic
            data = json.loads(response_text)
            return data
        except (ValueError, json.JSONDecodeError) as e:
            raise ValueError(f"Could not extract valid JSON from text: {e}") from e

    def get_signal(
        self,
        text: str,
        output_format: Literal['dict', 'NewsSignal'] = 'dict',
    ) -> dict | NewsSignal:
        """
        Get the news signal from the given `text`

        Args:
            text: The news article to get the signal from
            output_format: The format of the output

        Returns:
            The news signal
        """

        try:
            # Use chat completion and parse the JSON manually
            response = self.llm.complete(
                self.prompt_template.format(news_article=text)
            )

            parsed_response = self.extract_json(response.text)

            # Parse the JSON response
            # parsed_response = self.extract_json(response.text)

            # breakpoint()

            # Convert to NewsSignal
            news_signal = NewsSignal(
                btc_signal=parsed_response['btc_signal'],
                eth_signal=parsed_response['eth_signal'],
                reasoning=parsed_response['reasoning']
            )

        except Exception as e:
            print(f"Error occurred during request: {e}")
            raise

        if output_format == 'dict':
            return news_signal.to_dict()
        else:
            return news_signal



if __name__ == '__main__':
    from config import OllamaConfig

    config = OllamaConfig()

    llm = OllamaNewsSignalExtractor(
        llm_name=config.llm_name,
    )

    examples = [
        'Bitcoin ETF ads spotted on China’s Alipay payment app',
        'U.S. Supreme Court Lets Nvidia’s Crypto Lawsuit Move Forward',
        'Trump’s World Liberty Acquires ETH, LINK, and AAVE in $12M Crypto Shopping Spree',
    ]

    for example in examples:
        print(f'Example: {example}')
        response = llm.get_signal(example)
        print(response)

    """
    Example: Bitcoin ETF ads spotted on China’s Alipay payment app
    {
        "btc_signal": 1,
        "eth_signal": 0,
        'reasoning': "The news of Bitcoin ETF ads being spotted on China's Alipay payment
        app suggests a growing interest in Bitcoin and other cryptocurrencies among Chinese
        investors. This could lead to increased demand for BTC, causing its price to rise."
    }

    Example: U.S. Supreme Court Lets Nvidia’s Crypto Lawsuit Move Forward
    {
        'btc_signal': -1,
        'eth_signal': -1,
        'reasoning': "The US Supreme Court's decision allows Nvidia to pursue its crypto
        lawsuit, which could lead to increased regulatory uncertainty and potential
        restrictions on cryptocurrency mining. This could negatively impact the prices
        of both BTC and ETH."
    }

    Example: Trump’s World Liberty Acquires ETH, LINK, and AAVE in $12M Crypto Shopping Spree
    {
        'btc_signal': 0,
        'eth_signal': 1,
        'reasoning': "The acquisition of ETH by a major company like
        Trump's World Liberty suggests that there is increased demand for
        Ethereum, which could lead to an increase in its price."
    }
    """


