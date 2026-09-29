from elasticsearch import AsyncElasticsearch, BadRequestError

from app.config import settings


es_client = AsyncElasticsearch(settings.elasticsearch_url)

INDEX_NAME = "documents"


async def init_es() -> None:
    try:
        exists = await es_client.indices.exists(index=INDEX_NAME)
        if not exists:
            await es_client.indices.create(
                index="INDEX_NAME",
                body={
                    "mappings": {
                        "properties": {
                            "id": {"type": "integer"},
                            "text": {
                                "type": "text",
                                "analyzer": "russian"
                            }
                        }
                    }
                }
            )
            print(f"Index '{INDEX_NAME}' created successfully")
    except BadRequestError as e:
        print(f"Error during index creation: {e}")

async def index_document(doc_id: int, text: str) -> None:
    await es_client.index(
        index=INDEX_NAME,
        id=str(doc_id),
        body={
            "id": doc_id,
            "text": text
        }
    )

async def delete_document(doc_id: int) -> None:
    try:
        await es_client.delete(index=INDEX_NAME, id=str(doc_id))
    except Exception as e:
        print(f"Document {doc_id} not found in Elasticsearch for deletion: {e}")

async def search_document(query: str, limit: int = 20) -> list[int]:
    try:
        response = await es_client.search(
            index=INDEX_NAME,
            body={
                "query": {
                    "match": {
                        "text": {
                            "query": query,
                            "fuzziness": "AUTO"
                        }
                    }
                },
                "size": limit
            }
        )

        hits = response["hits"]["hits"]
        return [int(hit["_source"]["id"]) for hit in hits]
    except Exception as e:
        print(f"Elasticsearch search error: {e}")
        return []

async def close_es() -> None:
    await es_client.close()