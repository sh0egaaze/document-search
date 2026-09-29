import asyncio

from app.elasticsearch_client import (
    init_es,
    index_document,
    search_documents,
    delete_document,
    close_es
)


async def main():
    await init_es()

    print("Indexing test documents...")
    await index_document(101, "Моя первая попытка построить что-то нормальное, оцените")
    await index_document(102, "Новый боевой таз, смоляной кузов пикап")
    await index_document(103, "Начало положено, двигатель от BMW на Жигули")

    await asyncio.sleep(1)

    print("\nSearching for 'пикапы'...")
    results = await search_documents("пикапы")
    print(f"Found IDs: {results} (Expected [102])")

    print("\nSearching for 'жигали' (typo test)...")
    results = await search_documents("жигали")
    print(f"Found IDs: {results} (Expected [103])")

    print("\nDeleting document 102...")
    await delete_document(102)

    await asyncio.sleep(1)

    print("\nSearching for 'пикапы' after deletion...")
    results = await search_documents("пикапы")
    print(f"Found Ids: {results} (Expected [])")

    await close_es()
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())