"""Tests for the health check endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.asyncio
async def test_health_check_returns_200() -> None:
    """Test that health check endpoint returns 200 status code."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    print("INFO [TestHealth]: Health check returns 200 - PASSED")


@pytest.mark.asyncio
async def test_health_check_response_structure() -> None:
    """Test that health check response contains required fields."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/health")

    data = response.json()

    assert "status" in data
    assert "timestamp" in data
    assert "version" in data
    print("INFO [TestHealth]: Health check response structure - PASSED")


@pytest.mark.asyncio
async def test_health_check_status_healthy() -> None:
    """Test that health check returns healthy status."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/health")

    data = response.json()

    assert data["status"] == "healthy"
    print("INFO [TestHealth]: Health check status is healthy - PASSED")


@pytest.mark.asyncio
async def test_health_check_version() -> None:
    """Test that health check returns correct version."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/health")

    data = response.json()

    assert data["version"] == "1.0.0"
    print("INFO [TestHealth]: Health check version is 1.0.0 - PASSED")


@pytest.mark.asyncio
async def test_health_check_timestamp_format() -> None:
    """Test that health check timestamp is in ISO format."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/health")

    data = response.json()

    # ISO format timestamp should contain 'T' separator
    assert "T" in data["timestamp"]
    print("INFO [TestHealth]: Health check timestamp format - PASSED")
