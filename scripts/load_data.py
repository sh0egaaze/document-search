import asyncio
import csv
import ast
from datetime import datetime

from app.database import init_db, async_session, engine
from app.models import Document
from app.elasticsearch_client import init_es, index_document

CSV_FILE_PATH = "data/posts.csv"


async def load_data():
    print("Initializing Database...")
    await init_db()
    print("Initializing Elasticsearch Index...")
    await init_es()

    print(f"Reading data from {CSV_FILE_PATH}...")

    documents_to_insert = []

    with open(CSV_FILE_PATH, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for index, row in enumerate(reader, 1):
            try:
                created_date = datetime.strptime(row["created_date"], "%Y-%m-%d %H:%M:%S")
                rubrics = ast.literal_eval(row["rubrics"])

                doc = Document(
                    text=row["text"],
                    created_date=created_date,
                    rubrics=rubrics
                )
                documents_to_insert.append(doc)
            except Exception as e:
                print(f"Error parsing row {index}: {e}")

    if not documents_to_insert:
        print("No documents found to import.")
        return

    print(f"Parsed {len(documents_to_insert)} documents. Writing to PostgreSQL...")

    async with async_session() as session:
        session.add_all(documents_to_insert)
        await session.commit()

        es_tasks = []
        for doc in documents_to_insert:
            task = index_document(doc_id=doc.id, text=doc.text)
            es_tasks.append(task)

        print("Writing to Elasticsearch...")
        await asyncio.gather(*es_tasks)

    print("Data successfully loaded to PostgreSQL and Elasticsearch!")


async def main():
    try:
        await load_data()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())