# from typing import Literal, Optional

# from llms.base import BaseNewsSignalExtractor, NewsSignal
# from llama_index.core.prompts import PromptTemplate
# from llama_index.llms.anthropic import Anthropic


# class ClaudeNewsSignalExtractor(BaseNewsSignalExtractor):
#     def __init__(
#         self,
#         llm_name: str,
#         api_key: str,
#         temperature: Optional[float] = 0,
#     ):
#         self.llm = Anthropic(
#             model=llm_name,
#             api_key=api_key,
#             temperature=temperature,
#         )

#         self.prompt_template = PromptTemplate(
#             template="""
#             You are a financial analyst.
#             You are given a news article and you need to determine the impact of the news on the BTC and ETH price.

#             You need to output the signal in the following format:
#             {
#                 "btc_signal": 1,
#            p     "eth_signal": 0
#             }

#             The signal is either 1, 0, or -1.
#             1 means the price is expected to go up.
#             0 means the price is expected to stay the same.
#             -1 means the price is expected to go down.

#             Here is the news article:
#             {news_article}
#             """
#         )

#         self.llm_name = llm_name

#     def get_signal(
#         self,
#         text: str,
#         output_format: Literal['dict', 'NewsSignal'] = 'dict',
#     ) -> NewsSignal | dict:

#         response: NewsSignal = self.llm.structured_predict(
#             NewsSignal,
#             prompt=self.prompt_template,
#             news_article=text,
#         )

#         if output_format == 'dict':
#             return response.to_dict()
#         else:
#             return response


# if __name__ == '__main__':

#     from config import AnthropicConfig

#     config = AnthropicConfig()

#     llm = ClaudeNewsSignalExtractor(
#                     llm_name=config.llm_name,
#                     api_key=config.api_key,
#                 )

#     examples = [
#         'Bitcoin ETF ads spotted on China’s Alipay payment app',
#         'U.S. Supreme Court Lets Nvidia’s Crypto Lawsuit Move Forward',
#         'Trump’s World Liberty Acquires ETH, LINK, and AAVE in $12M Crypto Shopping Spree',
#     ]

#     for example in examples:
#         print(f'Example: {example}')
#         response = llm.get_signal(example)
#         print(response)

#     """
#     Example: Bitcoin ETF ads spotted on China’s Alipay payment app
#     {
#         'btc_signal': 1,
#         'eth_signal': 0,
#         'reasoning': "The appearance of Bitcoin ETF ads on China's Alipay, one of the
#         country's largest payment platforms, is significantly bullish for Bitcoin. This
#         suggests potential opening of the Chinese market to Bitcoin investment products,
#         which could drive substantial new demand given China's large investor base.
#         This is particularly notable given China's previous strict stance against cryptocurrencies.
#         For Ethereum, while crypto news can have ecosystem-wide effects, this news specifically
#         concerns Bitcoin ETFs and doesn't directly impact Ethereum's fundamentals or market
#         position, hence a neutral signal."
#     }

#     Example: U.S. Supreme Court Lets Nvidia’s Crypto Lawsuit Move Forward
#     {
#         'btc_signal': 0,
#         'eth_signal': 0,
#         'reasoning': "The Supreme Court's decision to allow a lawsuit against Nvidia to
#         proceed is primarily a corporate legal matter affecting Nvidia rather than
#         cryptocurrencies directly. The lawsuit concerns historical revenue reporting
#         practices and doesn't impact current cryptocurrency operations, mining capabilities,
#         or market fundamentals. While the news is crypto-related, it's unlikely to cause
#         any significant price movement in either BTC or ETH as it doesn't affect their
#         current utility, adoption, or regulatory status."
#     }

#     {
#         'btc_signal': 0,
#         'eth_signal': 1,
#         'reasoning': "Trump's World Liberty has made a $12M cryptocurrency purchase
#         focusing on ETH and ETH-ecosystem tokens (LINK, AAVE). This is directly positive
#         for ETH as it represents significant institutional buying pressure and strengthens
#         the Ethereum ecosystem. While large crypto purchases generally create positive market
#         sentiment, this news is specifically focused on ETH and its ecosystem,
#         making it neutral for BTC as attention might actually be drawn away from Bitcoin
#         to Ethereum in the short term."
#     }
#     """

from typing import Literal, Optional
import json

from llms.base import BaseNewsSignalExtractor, NewsSignal
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.anthropic import Anthropic


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

    def extract_json(self, text: str) -> dict:
        """
        Extract JSON from the response text using multiple methods
        """
        try:
            first_brace = text.index('{')
            last_brace = text.rindex('}')
            json_str = text[first_brace:last_brace+1]
            return json.loads(json_str)
        except (ValueError, json.JSONDecodeError):
            raise ValueError(f"Could not extract valid JSON from text: {text}")

    def get_signal(
        self,
        text: str,
        output_format: Literal['dict', 'NewsSignal'] = 'dict',
    ) -> NewsSignal | dict:
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

            # Parse the JSON response
            parsed_response = self.extract_json(response.text)

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

    from config import AnthropicConfig

    config = AnthropicConfig()

    llm = ClaudeNewsSignalExtractor(
        llm_name=config.llm_name,
        api_key=config.api_key,
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
        "reasoning": "The news of Bitcoin ETF ads being spotted on China's Alipay payment
        app suggests a growing interest in Bitcoin and other cryptocurrencies among Chinese
        investors. This could lead to increased demand for BTC, causing its price to rise."
    }

    Example: U.S. Supreme Court Lets Nvidia’s Crypto Lawsuit Move Forward
    {
        "btc_signal": -1,
        "eth_signal": -1,
        "reasoning": "The US Supreme Court's decision allows Nvidia to pursue its crypto
        lawsuit, which could lead to increased regulatory uncertainty and potential
        restrictions on cryptocurrency mining. This could negatively impact the prices
        of both BTC and ETH."
    }

    Example: Trump’s World Liberty Acquires ETH, LINK, and AAVE in $12M Crypto Shopping Spree
    {
        "btc_signal": 0,
        "eth_signal": 1,
        "reasoning": "The acquisition of ETH by a major company like
        Trump's World Liberty suggests that there is increased demand for
        Ethereum, which could lead to an increase in its price."
    }
    """
