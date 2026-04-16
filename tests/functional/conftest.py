"""Fixtures para tests funcionales contra la API desplegada."""

import httpx
import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Agrega --base-url como opción de CLI para pytest."""
    parser.addoption(
        "--base-url",
        action="store",
        default="",
        help="URL base de la API desplegada (ej: https://...app.github.dev)",
    )


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    """URL base de la API desplegada, desde --base-url."""
    url = request.config.getoption("--base-url")
    if not url:
        pytest.skip("--base-url no proporcionada. Tests funcionales requieren API desplegada.")
    return url.rstrip("/")


@pytest.fixture(scope="session")
def api_client(base_url: str) -> httpx.Client:
    """Cliente httpx apuntando a la API desplegada."""
    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        yield client


@pytest.fixture()
def context() -> dict:
    """Diccionario limpio por test para compartir estado entre steps."""
    return {}
