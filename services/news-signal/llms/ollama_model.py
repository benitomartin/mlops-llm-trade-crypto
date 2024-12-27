import json
from typing import Literal, Optional

from llama_index.core.prompts import PromptTemplate
from llama_index.llms.ollama import Ollama
from llms.base import BaseNewsSignalExtractor, NewsSignal
from loguru import logger


class OllamaNewsSignalExtractor(BaseNewsSignalExtractor):
    def __init__(
        self,
        llm_name: str,
        base_url: str,
        temperature: Optional[float] = 0,
    ):
        self.llm = Ollama(
            model=llm_name,
            temperature=temperature,
            base_url=base_url,

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
        output_format: Literal['list', 'NewsSignal'] = 'list',
    ) -> NewsSignal | list[dict] | None:
        try:
            # Use chat completion and parse the JSON manually
            response = self.llm.complete(self.prompt_template.format(news_article=text))
            print(f"Response: {response}")
            print(f"Response text: {response.text}")

            # Parse the JSON response
            # Clean the response text to handle trailing commas
            raw_response = response.text
            clean_response = raw_response.replace(",\n]", "\n]")  # Remove trailing comma in JSON lists
            print(f"Cleaned response: {clean_response}")

            # breakpoint()
            # Check for exactly one set of outer brackets
            if clean_response.count('[') != 1 or clean_response.count(']') != 1:
                logger.warning("Response does not match expected array structure")
                return []

            # Validate basic JSON array structure with proper coin/signal format
            import re

            # Check if the response matches the expected structure
            pattern = r'\[\s*({.*?}(?:\s*,\s*{.*?})*)\s*\]'
            if not re.match(pattern, clean_response, re.DOTALL):
                logger.warning("Response does not match expected array structure")
                return []

            # Additional validation for each object's structure
            entries = re.findall(r'{[^{}]+}', clean_response)
            valid_entries = []

            for entry in entries:
                # Check if entry contains only "coin" and "signal" keys with proper format
                if re.match(r'\s*{\s*"coin"\s*:\s*"[^"]+"\s*,\s*"signal"\s*:\s*-?\d+\s*}\s*', entry):
                    valid_entries.append(entry)

            if not valid_entries:
                logger.warning("No valid entries found in response")
                return []

            # Reconstruct valid JSON array
            valid_json = f"[{','.join(valid_entries)}]"

            # Now parse the validated JSON
            parsed_response = json.loads(valid_json)

            # Create NewsSignal with the validated responses
            news_signal = NewsSignal(news_signals=parsed_response)

            if output_format == 'list':
                return news_signal.model_dump()['news_signals']
            else:
                return news_signal

        except Exception as e:
            print(f'Error occurred during request: {e}')
            raise


if __name__ == '__main__':
    from config import OllamaConfig

    config = OllamaConfig()

    llm = OllamaNewsSignalExtractor(
        llm_name=config.llm_name,
        base_url=config.ollama_base_url,
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
