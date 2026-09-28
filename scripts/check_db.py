import asyncio
from datetime import datetime

from sqlalchemy import select, delete

from app.database import init_db, engine, async_session
from app.models import Document


async def main():
    await init_db()
    print("Tables created")

    test_doc = Document(
        rubrics=["VK-123", "VK-456"],
        text="Тестовый документ для проверки",
        created_date=datetime.now()
    )

    async with async_session() as session:
        session.add(test_doc)
        await session.commit()
        print(f"Doc created with id={test_doc.id}")

    async with async_session() as session:
        stmt = select(Document).where(Document.id == test_doc.id)
        result = await session.execute(stmt)
        doc = result.scalar_one()
        print(f"Read from db: {doc}")

    async with async_session() as session:
        stmt = delete(Document).where(Document.id == test_doc.id)
        await session.execute(stmt)
        await session.commit()
        print(f"Delete document with id={test_doc.id}")

    await engine.dispose()
    print("Dispose engine")

if __name__ == "__main__":
    asyncio.run(main())