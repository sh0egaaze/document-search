import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

async def test_search_found(client: AsyncClient):
    response = await client.post("/search", json={"query": "bmw"})
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "results" in data
    assert data["total"] > 0
    assert "id" in data["results"][0]
    assert "text" in data["results"][0]
    assert "rubrics" in data["results"][0]
    assert "created_date" in data["results"][0]

async def test_search_not_found(client: AsyncClient):
    response = await client.post("/search", json={"query": "sdgdfgshtrtfs4563453gr"})
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "results" in data
    assert data["total"] == 0
    assert data["results"] == []

async def test_empty_search(client: AsyncClient):
    response = await client.post("/search", json={"query": ""})
    assert response.status_code == 200

async def test_invalid_search(client: AsyncClient):
    response = await client.post("/search", json={})
    assert response.status_code == 422

async def test_successful_deletion(client: AsyncClient):
    search_response = await client.post("/search", json={"query": "жИгА"})
    assert search_response.status_code == 200
    search_data = search_response.json()
    assert search_data["total"] > 0

    doc_id = search_data["results"][0]["id"]

    delete_response = await client.delete(f"/documents/{doc_id}")
    assert delete_response.status_code == 200
    delete_data = delete_response.json()
    assert delete_data["id"] == doc_id
    assert "message" in delete_data

async def test_delete_not_found(client: AsyncClient):
    response = await client.delete(f"/documents/999999")
    assert response.status_code == 404

async def test_deleted_document_not_searchable(client: AsyncClient):
    search_response = await client.post("/search", json={"query": "анон"})
    assert search_response.status_code == 200
    search_data = search_response.json()
    assert search_data["total"] > 0

    doc_id = search_data["results"][0]["id"]

    delete_response = await client.delete(f"/documents/{doc_id}")
    assert delete_response.status_code == 200
    delete_data = delete_response.json()
    assert delete_data["id"] == doc_id
    assert "message" in delete_data

    await asyncio.sleep(1)

    search_response = await client.post("/search", json={"query": "анон"})
    assert search_response.status_code == 200
    search_data = search_response.json()

    result_ids = [doc["id"] for doc in search_data["results"]]
    assert doc_id not in result_ids