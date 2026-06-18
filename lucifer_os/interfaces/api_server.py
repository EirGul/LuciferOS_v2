from dataclasses import asdict

from fastapi import FastAPI

from lucifer_os.interfaces.api_schema import ApiChatRequest
from lucifer_os.interfaces.api_service import ApiService


def create_api_app(
    project_root: str = '.',
    provider_name: str | None = None,
) -> FastAPI:
    service = ApiService(project_root=project_root, provider_name=provider_name)
    app = FastAPI(title='LuciferOS API')

    @app.get('/health')
    def health() -> dict:
        return asdict(service.health())

    @app.post('/chat')
    def chat(request: ApiChatRequest) -> dict:
        response = service.chat(request)
        return asdict(response)

    return app


app = create_api_app()


def main() -> None:
    import uvicorn

    uvicorn.run(
        'lucifer_os.interfaces.api_server:app',
        host='127.0.0.1',
        port=8787,
        reload=False,
    )


if __name__ == '__main__':
    main()
