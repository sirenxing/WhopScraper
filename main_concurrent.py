import asyncio
import threading
import requests

async def fetch_options_data():
    print("Fetching options data...")
    # Implement your options fetching logic here
    await asyncio.sleep(2)  # Simulate I/O work
    print("Options data fetched!")

async def fetch_stocks_data():
    print("Fetching stocks data...")
    # Implement your stocks fetching logic here
    await asyncio.sleep(2)  # Simulate I/O work
    print("Stocks data fetched!")

async def monitor():
    options_task = asyncio.create_task(fetch_options_data())
    stocks_task = asyncio.create_task(fetch_stocks_data())
    await options_task
    await stocks_task

if __name__ == '__main__':
    # Use threading to run the asyncio event loop
    loop = asyncio.get_event_loop()
    thread = threading.Thread(target=loop.run_until_complete, args=(monitor(),))
    thread.start()
    thread.join()