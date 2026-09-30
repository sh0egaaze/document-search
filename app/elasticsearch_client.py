from elasticsearch import AsyncElasticsearch, BadRequestError

from app.config import settings


INDEX_NAME = "documents"

def get_es() -> AsyncElasticsearch:
    return AsyncElasticsearch(settings.elasticsearch_url)


async def init_es() -> None:
    es = get_es()
    try:
        exists = await es.indices.exists(index=INDEX_NAME)
        if not exists:
            await es.indices.create(
                index=INDEX_NAME,
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
    finally:
        await es.close()

async def index_document(doc_id: int, text: str) -> None:
    es = get_es()
    try:
        await es.index(
            index=INDEX_NAME,
            id=str(doc_id),
            body={
                "id": doc_id,
                "text": text
            }
        )
    finally:
        await es.close()

async def delete_document(doc_id: int) -> None:
    es = get_es()
    try:
        await es.delete(index=INDEX_NAME, id=str(doc_id))
    except Exception as e:
        print(f"Document {doc_id} not found in Elasticsearch for deletion: {e}")
    finally:
        await es.close()

async def search_documents(query: str, limit: int = 20) -> list[int]:
    es = get_es()
    try:
        response = await es.search(
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
    finally:
        await es.close()