from typing import Optional

import pandas as pd
from quixstreams.sources.base import Source

from .news import News


class HistoricalNewsDataSource(Source):
    def __init__(
        self,
        url_rar_file: Optional[str] = None,
        path_to_csv_file: Optional[str] = None,
    ):
        super().__init__(name='news_historical_data_source')
        self.url_rar_file = url_rar_file
        self.path_to_csv_file = path_to_csv_file

        if self.url_rar_file:
            self.path_to_csv_file = self._download_and_extract_rar_file(
                self.url_rar_file
            )

        if not self.path_to_csv_file:
            if not self.url_rar_file:
                raise ValueError(
                    'Either url_rar_file or path_to_csv_file must be provided'
                )

    def _download_and_extract_rar_file(self, url_rar_file: str) -> str:
        """
        Downloads a RAR file from a URL, extracts it, and returns the path to the first CSV file found.

        Args:
            url_rar_file (str): URL of the RAR file to download

        Returns:
            str: Path to the extracted CSV file

        Raises:
            Exception: If no CSV file is found in the RAR archive
        """
        # TODO: implement this function
        raise NotImplementedError('Not implemented')

    def run(self):
        while self.running:
            # load the CSV file into a pandas dataframe
            df = pd.read_csv(self.path_to_csv_file)

            # drop nan values
            df = df.dropna()

            # convert the dataframe into a list of dictionaries
            rows = df[['title', 'sourceId', 'newsDatetime']].to_dict(orient='records')

            for row in rows:
                # transform raw data into News object
                news = News.from_csv_row(
                    title=row['title'],
                    source_id=row['sourceId'],
                    news_datetime=row['newsDatetime'],
                )

                # serialize the News object into a JSON string
                msg = self.serialize(
                    key='',
                    value=news.to_dict(),
                )

                # push message to internal Kafka topic that acts like a bridge
                # between my source and the Quix Streams Applicaton object that
                # uses this source to ingest data
                #   # run.py
                #   sdf = app.dataframe(source=news_source)
                self.produce(
                    key=msg.key,
                    value=msg.value,
                )


if __name__ == '__main__':
    source = HistoricalNewsDataSource(
        path_to_csv_file='./data/cryptopanic_news.csv',
    )
    source.run()
