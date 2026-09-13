import uvicorn
from app.config import settings

if __name__ == "__main__":
    print("=" * 65)
    print(f"  {settings.API_TITLE} v{settings.API_VERSION}")
    print("=" * 65)
    print(f"  * Server running at:       http://{settings.HOST}:{settings.PORT}")
    print(f"  * Interactive Swagger UI:  http://{settings.HOST}:{settings.PORT}/docs")
    print(f"  * Alternative ReDoc UI:    http://{settings.HOST}:{settings.PORT}/redoc")
    print("=" * 65)
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
