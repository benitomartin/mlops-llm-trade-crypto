from typing import Literal

from llms.base import BaseNewsSignalExtractor, NewsSignal


class DummyNewsSignalExtractor(BaseNewsSignalExtractor):
    """
    A dummy news signal that is super stupid, but works fast.
    I added this so I can run the backfill pipeline without having to wait for the LLM to respond.
    """

    def __init__(self):
        self.llm_name = 'dummy'

    def get_signal(
        self,
        text: str,
        output_format: Literal['list', 'NewsSignal'] = 'list',
    ) -> list[dict] | NewsSignal:
        """
        Always returns a NewsSignal with a signal of 1 for BTC and 0 for ETH

        Args:
            text: The news article to get the signal from
            output_format: The format of the output

        Returns:
            The news signal
        """
        if output_format == 'list':
            return [
                {
                    'coin': 'BTC',
                    'signal': 1,
                },
                {
                    'coin': 'ETH',
                    'signal': -1,
                },
            ]
        else:
            raise NotImplementedError(
                'Only list output format is supported for DummyNewsSignalExtractor'
            )



if __name__ == '__main__':


    llm = DummyNewsSignalExtractor(

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
