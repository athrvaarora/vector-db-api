"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .api.endpoints import router


def get_custom_swagger_ui_html():
    """Clean, minimal Swagger UI styling with proper markdown rendering."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vector Database API - Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui.css" />
        <link rel="icon" type="image/png" href="https://fastapi.tiangolo.com/img/favicon.png" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            html, body { 
                margin: 0; 
                padding: 0; 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                background: #fafbfc;
                color: #2d3748;
            }
            
            .swagger-ui { 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            
            .swagger-ui .topbar { 
                background: linear-gradient(135deg, #a688ff, #6ee7b7);
                border-bottom: 1px solid #e3d3ff;
                padding: 20px 0;
                box-shadow: 0 2px 8px rgba(166, 136, 255, 0.15);
            }
            
            .swagger-ui .topbar .download-url-wrapper { display: none; }
            
            .swagger-ui .info { 
                margin: 50px 0; 
                text-align: center;
            }
            
            .swagger-ui .info .title { 
                color: #2d3748; 
                font-size: 2.5rem; 
                font-weight: 700;
                margin-bottom: 20px;
                background: linear-gradient(135deg, #a688ff, #6ee7b7);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .swagger-ui .info .description { 
                color: #5c6570; 
                font-size: 1.125rem; 
                line-height: 1.75;
                max-width: 800px;
                margin: 0 auto;
                font-weight: 400;
            }
            
            /* Enhanced markdown rendering */
            .swagger-ui .info .description p {
                margin: 16px 0;
                text-align: left;
            }
            
            .swagger-ui .info .description h1,
            .swagger-ui .info .description h2,
            .swagger-ui .info .description h3 {
                color: #2d3748;
                font-weight: 600;
                margin: 24px 0 12px 0;
            }
            
            .swagger-ui .info .description h2 {
                font-size: 1.5rem;
                border-bottom: 2px solid #e3d3ff;
                padding-bottom: 8px;
            }
            
            .swagger-ui .info .description h3 {
                font-size: 1.25rem;
                color: #a688ff;
            }
            
            .swagger-ui .info .description ul {
                text-align: left;
                margin: 12px 0;
                padding-left: 24px;
            }
            
            .swagger-ui .info .description li {
                margin: 8px 0;
                line-height: 1.6;
            }
            
            .swagger-ui .info .description strong {
                color: #2d3748;
                font-weight: 600;
            }
            
            .swagger-ui .info .description code {
                background: #f0e7ff;
                color: #7c3aed;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 0.875rem;
                font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
            }
            
            .swagger-ui .scheme-container { 
                background: #ffffff; 
                border: 1px solid #e3e7eb;
                border-radius: 12px;
                padding: 20px;
                margin: 24px 0;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            
            .swagger-ui .opblock { 
                border-radius: 12px; 
                margin: 16px 0;
                border: 1px solid #e3e7eb;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            }
            
            .swagger-ui .opblock.opblock-post { 
                border-left: 4px solid #22c55e; 
            }
            
            .swagger-ui .opblock.opblock-get { 
                border-left: 4px solid #a688ff; 
            }
            
            .swagger-ui .opblock.opblock-put { 
                border-left: 4px solid #ec7085; 
            }
            
            .swagger-ui .opblock.opblock-delete { 
                border-left: 4px solid #f59e0b; 
            }
            
            .swagger-ui .opblock .opblock-summary { 
                padding: 20px;
                background: #ffffff;
                border-bottom: 1px solid #f1f3f6;
            }
            
            .swagger-ui .opblock .opblock-summary .opblock-summary-method {
                border-radius: 8px;
                font-weight: 600;
                font-size: 11px;
                padding: 6px 12px;
                min-width: 70px;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .swagger-ui .btn { 
                border-radius: 8px; 
                font-weight: 500;
                transition: all 0.2s ease;
                font-size: 14px;
                padding: 10px 20px;
                border: none;
            }
            
            .swagger-ui .btn.execute { 
                background: linear-gradient(135deg, #a688ff, #8b5cf6);
                color: white;
                box-shadow: 0 2px 8px rgba(166, 136, 255, 0.25);
            }
            
            .swagger-ui .btn.execute:hover { 
                background: linear-gradient(135deg, #8b5cf6, #7c3aed);
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(166, 136, 255, 0.35);
            }
            
            .swagger-ui .parameters-col_description p,
            .swagger-ui .response-col_description p { 
                color: #5c6570; 
                line-height: 1.6;
                font-size: 14px;
                margin: 8px 0;
            }
            
            .swagger-ui .model-box { 
                border-radius: 8px; 
                background: #f8f9fb;
                border: 1px solid #e3e7eb;
                margin: 12px 0;
            }
            
            .swagger-ui .model .model-title { 
                color: #2d3748; 
                font-weight: 600;
                font-size: 16px;
            }
            
            .swagger-ui .parameter__name { 
                font-weight: 600; 
                color: #2d3748;
            }
            
            .swagger-ui .response-control-media-type__title { 
                font-weight: 600; 
                color: #2d3748;
            }
            
            .swagger-ui .tab { 
                border-radius: 8px 8px 0 0; 
                font-weight: 500;
                padding: 12px 16px;
            }
            
            .swagger-ui .tab.active { 
                background: linear-gradient(135deg, #a688ff, #8b5cf6);
                color: white;
            }
            
            .swagger-ui input[type=text], 
            .swagger-ui input[type=password], 
            .swagger-ui input[type=search], 
            .swagger-ui input[type=email], 
            .swagger-ui input[type=url] { 
                border-radius: 8px; 
                border: 2px solid #e3e7eb;
                transition: all 0.2s ease;
                padding: 10px 14px;
                font-size: 14px;
                background: #ffffff;
            }
            
            .swagger-ui input:focus { 
                border-color: #a688ff; 
                box-shadow: 0 0 0 3px rgba(166, 136, 255, 0.1);
                outline: none;
            }
            
            .swagger-ui .response .response-content { 
                border-radius: 8px; 
                margin: 12px 0;
            }
            
            .swagger-ui .highlight-code .microlight { 
                border-radius: 8px; 
                background: #2d3748 !important;
                font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
                padding: 16px;
                line-height: 1.5;
            }
            
            .swagger-ui .wrapper { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 30px;
            }
            

            
            /* Enhanced tag display */
            .swagger-ui .opblock-tag {
                font-size: 18px !important;
                font-weight: 600 !important;
                color: #2d3748 !important;
                margin: 24px 0 16px 0 !important;
                padding: 12px 0 !important;
                border-bottom: 2px solid #e3e7eb !important;
            }
            
            /* Better operation grouping */
            .swagger-ui .opblock-tag-section {
                margin: 24px 0 !important;
            }
            
            /* Hide unnecessary elements */
            .swagger-ui .info .title small { display: none; }
            .swagger-ui .scheme-container .schemes-title { display: none; }
            
            /* Loading animation */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .swagger-ui .wrapper {
                animation: fadeIn 0.6s ease-out;
            }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"></script>
        <script>
            const ui = SwaggerUIBundle({
                url: '/openapi.json',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ],
                layout: "BaseLayout",
                deepLinking: true,
                showExtensions: true,
                showCommonExtensions: true,
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1,
                docExpansion: "list",
                filter: false,
                tryItOutEnabled: true,
                displayOperationId: false,
                displayRequestDuration: true,
                supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
                onComplete: function(swaggerApi, swaggerUi) {
                    console.log("Swagger UI loaded successfully");
                    
                    // Check if spec loaded properly
                    if (swaggerApi && swaggerApi.spec && swaggerApi.spec.paths) {
                        const pathCount = Object.keys(swaggerApi.spec.paths).length;
                        console.log(`OpenAPI spec loaded with ${pathCount} paths`);
                    } else {
                        console.error("OpenAPI spec not loaded properly");
                    }
                },
                requestInterceptor: (request) => {
                    if (request.url.includes('/openapi.json')) {
                        console.log('Loading OpenAPI spec...');
                    }
                    return request;
                },
                responseInterceptor: (response) => {
                    if (response.url.includes('/openapi.json')) {
                        console.log('OpenAPI spec loaded successfully');
                    }
                    return response;
                },
                // Enhanced markdown support
                syntaxHighlight: {
                    activate: true,
                    theme: "agate"
                },
                // Validation options
                validatorUrl: null
            });
            

        </script>
    </body>
    </html>
    """


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Vector Database API",
        description="""
# Vector Database Platform

A high-performance REST API for indexing and querying documents using semantic vector search.

## Features

- **Library Management**: Organize documents into collections
- **Document Operations**: Full CRUD operations for documents
- **Chunk Processing**: Break documents into searchable chunks
- **Vector Search**: Semantic similarity search using embeddings
- **Multiple Indexes**: Flat, LSH, and Hierarchical indexing algorithms
- **Thread Safety**: Concurrent read/write operations

## Architecture

- **Domain-Driven Design**: Clean separation of concerns
- **Service Layer**: Business logic isolation
- **Multiple Algorithms**: Pluggable indexing strategies
- **Real Embeddings**: Cohere API integration

## API Endpoints

Explore the interactive documentation below to test all endpoints.
        """,
        version="1.0.0",
        openapi_version="3.0.2",
        docs_url=None,  # Disable default docs
        redoc_url="/redoc",
        openapi_tags=[
            {
                "name": "Libraries",
                "description": "Create and manage document libraries. Libraries are collections that organize documents and provide access control."
            },
            {
                "name": "Documents", 
                "description": "CRUD operations for documents within libraries. Documents contain metadata and are broken into searchable chunks."
            },
            {
                "name": "Chunks",
                "description": "Manage document chunks for vector search. Chunks are the atomic units of text that get indexed and searched."
            },
            {
                "name": "Indexing",
                "description": "Build vector indexes for libraries using different algorithms (Flat, LSH, Hierarchical)."
            },
            {
                "name": "Search",
                "description": "Perform semantic similarity search using vector embeddings to find relevant content."
            },
            {
                "name": "Utilities",
                "description": "Helper endpoints for embeddings generation and other utility functions."
            },
            {
                "name": "Health",
                "description": "System health and status monitoring endpoints."
            }
        ],
        servers=[
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            }
        ]
    )
    
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return HTMLResponse(get_custom_swagger_ui_html())
    
    # Add CORS middleware for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(router, prefix="/api/v1")
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)