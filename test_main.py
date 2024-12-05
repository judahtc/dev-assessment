import pytest
from fastapi import HTTPException
from httpx import RequestError
import httpx
from main import get_user_gists


@pytest.mark.asyncio
async def test_get_user_gists_success(monkeypatch):
    # Mock successful response data
    mock_gists = [
        {
            "id": "6cad326836d38bd3a7ae",
            "description": "Hello world!",
            "url": "https://gist.github.com/octocat/6cad326836d38bd3a7ae"
        },
        {
            "id": "0831f3fbd83ac4d46451",
            "description": "",
            "url": "https://gist.github.com/octocat/0831f3fbd83ac4d46451"
        },
        {
            "id": "2a6851cde24cdaf4b85b",
            "description": "",
            "url": "https://gist.github.com/octocat/2a6851cde24cdaf4b85b"
        },
        {
            "id": "9257657",
            "description": "Some common .gitignore configurations",
            "url": "https://gist.github.com/octocat/9257657"
        },
        {
            "id": "1305321",
            "description": 'null',
            "url": "https://gist.github.com/octocat/1305321"
        },
        {
            "id": "1169854",
            "description": None,
            "url": "https://gist.github.com/octocat/1169854"
        },
        {
            "id": "1169852",
            "description": None,
            "url": "https://gist.github.com/octocat/1169852"
        },
        {
            "id": "1162032",
            "description": None,
            "url": "https://gist.github.com/octocat/1162032"
        }

    ]

    class MockResponse:
        status_code = 200

        def json(self):
            return mock_gists

    class MockAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url):
            return MockResponse()

    # Patch httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    # Test the function
    result = await get_user_gists("octocat")

    assert len(result) == 2
    assert result[0]["id"] == "1"
    assert result[0]["description"] == "Test Gist 1"
    assert result[0]["url"] == "https://gist.github.com/octocat/1"
    # Testing default description
    assert result[1]["description"] == "No description"


@pytest.mark.asyncio
async def test_get_user_gists_user_not_found(monkeypatch):
    class MockResponse:
        status_code = 404

        def json(self):
            return {"message": "Not Found"}

    class MockAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url):
            return MockResponse()

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    with pytest.raises(HTTPException) as exc_info:
        await get_user_gists("nonexistent-user")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


@pytest.mark.asyncio
async def test_get_user_gists_api_error(monkeypatch):
    class MockAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url):
            raise RequestError("Connection error")

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    with pytest.raises(HTTPException) as exc_info:
        await get_user_gists("octocat")

    assert exc_info.value.status_code == 500
    assert "Error connecting to GitHub API" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_user_gists_other_error(monkeypatch):
    class MockResponse:
        status_code = 403

        def json(self):
            return {"message": "Rate limit exceeded"}

    class MockAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url):
            return MockResponse()

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    with pytest.raises(HTTPException) as exc_info:
        await get_user_gists("octocat")

    assert exc_info.value.status_code == 403
    assert exc_info.value.json() == {"message": "Rate limit exceeded"}
