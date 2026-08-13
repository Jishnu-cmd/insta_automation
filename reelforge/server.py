import os
import sys
import uvicorn
from reelforge.config import settings

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    print("=========================================================")
    print(f"  ReelForge AI Platform Starting")
    print(f"  Account: {settings.INSTAGRAM_HANDLE} ({settings.BRAND_NAME})")
    print(f"  Binding to: http://{host}:{port}")
    print("=========================================================")
    
    uvicorn.run("reelforge.api.main:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
