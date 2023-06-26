import aiohttp
from pandas import DataFrame


async def load(df: DataFrame):
    """Send data to httpbin without saving csv file to disk"""
    df_str = df.to_csv(None)  # returns csv as string
    async with aiohttp.ClientSession() as session:
        async with session.post("https://httpbin.org/post", data=df_str.encode('UTF-8')) as resp:
            print(resp.status)
            print(await resp.text())
