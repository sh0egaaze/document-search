from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_session, init_db
from app import models, schemas
from app.elasticsearch_client import init_es, search_documents, delete_document


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initialization DB...")
    await init_db()

    print("Initialization Elasticsearch...")
    await init_es()
    print("Application successfully started!")

    yield

    print("Application stopped.")


app = FastAPI(title="Поисковик документов", lifespan=lifespan)


@app.post("/search", response_model=schemas.SearchResponse)
async def search(
        request: schemas.SearchRequest,
        session: AsyncSession = Depends(get_session)
) -> schemas.SearchResponse:
    matched_ids: list[int] = await search_documents(query=request.query, limit=20)

    if not matched_ids:
        return schemas.SearchResponse(total=0, results=[])

    stmt = select(models.Document).where(models.Document.id.in_(matched_ids))

    result = await session.execute(stmt)
    documents = result.scalars().all()

    sorted_documents = sorted(
        documents,
        key=lambda doc: doc.created_date,
        reverse=True
    )

    return schemas.SearchResponse(
        total=len(sorted_documents),
        results=sorted_documents
    )

@app.delete("/documents/{document_id}", response_model=schemas.DeleteResponse)
async def delete_document_route(
        document_id: int,
        session: AsyncSession = Depends(get_session)
) -> schemas.DeleteResponse:
    document = await session.get(models.Document, document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    await session.delete(document)
    await session.commit()

    await delete_document(doc_id=document_id)

    return schemas.DeleteResponse(
        message="Document deleted successfully",
        id=document_id
    )