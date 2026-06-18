from dataclasses import asdict
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lucifer_os.interfaces.api_schema import ApiChatRequest
from lucifer_os.interfaces.api_service import ApiService


def resolve_api_provider_name(provider_name: str | None = None) -> str | None:
    if provider_name is not None:
        cleaned_provider_name = provider_name.strip().lower()
        return cleaned_provider_name or None

    env_provider_name = os.environ.get("LUCIFER_PROVIDER", "").strip().lower()
    return env_provider_name or None


def create_api_app(
    project_root: str = ".",
    provider_name: str | None = None,
) -> FastAPI:
    resolved_provider_name = resolve_api_provider_name(provider_name)
    service = ApiService(project_root=project_root, provider_name=resolved_provider_name)
    app = FastAPI(title="LuciferOS API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:8787",
            "http://localhost:8787",
            "file://",
            "null",
        ],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    @app.get("/health")
    def health() -> dict:
        return asdict(service.health())

    @app.post("/chat")
    def chat(request: ApiChatRequest) -> dict:
        response = service.chat(request)
        return asdict(response)

    return app


app = create_api_app()


def main() -> None:
    import uvicorn

    uvicorn.run(
        "lucifer_os.interfaces.api_server:app",
        host="127.0.0.1",
        port=8787,
        reload=False,
    )


if __name__ == "__main__":
    main()
