from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.routes import design, projects, experiences, data, portfolio, contact, profile
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(design.router, prefix=f"{settings.API_V1_STR}/design", tags=["design"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(experiences.router, prefix=f"{settings.API_V1_STR}/experiences", tags=["experiences"])
app.include_router(data.router, prefix=f"{settings.API_V1_STR}/data", tags=["data"])
app.include_router(portfolio.router, prefix=f"{settings.API_V1_STR}/portfolio", tags=["portfolio"])
app.include_router(contact.router, prefix=f"{settings.API_V1_STR}/contact", tags=["contact"])
app.include_router(profile.router, prefix=f"{settings.API_V1_STR}/contact", tags=["profile"])


@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Design System API</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 2rem;
                    line-height: 1.6;
                }
                a {
                    color: #0066cc;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
                .endpoints {
                    background-color: #f5f5f5;
                    padding: 1rem;
                    border-radius: 0.5rem;
                }
            </style>
        </head>
        <body>
            <h1>Design System API</h1>
            <p>Welcome to the Design System API. This API provides endpoints for managing design systems and dynamic data.</p>
            
            <h2>Documentation</h2>
            <p>
                <a href="/docs">Swagger UI</a> - Interactive API documentation
                <br>
                <a href="/redoc">ReDoc</a> - Alternative API documentation
            </p>
            
            <h2>Main Endpoints</h2>
            <div class="endpoints">
                <h3>Design System</h3>
                <ul>
                    <li><code>GET /api/v1/design/</code> - List all design systems</li>
                    <li><code>GET /api/v1/design/active</code> - Get the active design system</li>
                    <li><code>POST /api/v1/design/</code> - Create a new design system</li>
                    <li><code>PUT /api/v1/design/{id}</code> - Update a design system</li>
                    <li><code>POST /api/v1/design/{id}/activate</code> - Activate a design system</li>
                </ul>
                
                <h3>Dynamic Data</h3>
                <ul>
                    <li><code>GET /api/v1/data/</code> - List all data items</li>
                    <li><code>GET /api/v1/data/search?q={query}</code> - Search data items</li>
                    <li><code>POST /api/v1/data/</code> - Create a new data item</li>
                    <li><code>PUT /api/v1/data/{id}</code> - Update a data item</li>
                    <li><code>DELETE /api/v1/data/{id}</code> - Delete a data item</li>
                </ul>
            </div>
        </body>
    </html>
    """

# @app.get("/api/v1/css", response_class=FileResponse)
# async def get_css():
#     """Generate and return CSS variables based on the active design system"""
#     # In a real application, you would generate this dynamically
#     # For now, we'll return a static CSS file
#     return FileResponse("app/static/css/styles.css")