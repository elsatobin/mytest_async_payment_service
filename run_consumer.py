import asyncio
from app.broker import broker
from app.consumer import router

broker.include_router(router)

async def main():
    await broker.start()

if __name__ == "__main__":
    asyncio.run(main())