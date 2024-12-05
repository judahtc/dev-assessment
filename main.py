from typing import Union
import httpx

from fastapi import FastAPI, HTTPException

app = FastAPI()
GITHUB_API_BASE_URL = "https://api.github.com"


@app.get("/{username}")
async def get_user_gists(username: str):

    url = f"{GITHUB_API_BASE_URL}/users/{username}/gists"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        if response.status_code == 200:
            gists = response.json()
            # Extract relevant data from each gist
            return [
                {
                    "id": gist["id"],
                    "description": gist.get("description", "No description"),
                    "url": gist["html_url"],
                }
                for gist in gists
            ]
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            raise HTTPException(
                status_code=response.status_code, detail=response.json())
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500, detail=f"Error connecting to GitHub API: {exc}")
