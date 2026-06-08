"""Convenience launcher.  Run:  python run.py"""
import uvicorn
from backend.config import settings

if __name__ == "__main__":
    print("=" * 64)
    print(f"  {settings.APP_NAME} v{settings.VERSION}  -  by {settings.VENDOR}")
    print(f"  App   :  http://localhost:{settings.PORT}")
    print(f"  Login :  http://localhost:{settings.PORT}/login")
    print(f"  Docs  :  http://localhost:{settings.PORT}/docs")
    print(f"  Demo  :  {settings.DEMO_EMAIL} / {settings.DEMO_PASSWORD}")
    print("=" * 64)
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=False)
