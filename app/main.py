"""
Main FastAPI application for Digital Social Score API.
Detects text toxicity with GDPR compliance and observability.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import logging
import time
from contextlib import asynccontextmanager

from app.models import TextAnalysisRequest, TextAnalysisResponse, HealthResponse
from app.toxicity_detector import ToxicityDetector
from app.gdpr_handler import GDPRHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method', 'status'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'Request duration', ['endpoint'])
TOXICITY_SCORE = Histogram('toxicity_score', 'Distribution of toxicity scores')

# Global instances
toxicity_detector = None
gdpr_handler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources."""
    global toxicity_detector, gdpr_handler
    
    logger.info("Starting application initialization...")
    toxicity_detector = ToxicityDetector()
    gdpr_handler = GDPRHandler()
    logger.info("Application initialized successfully")
    
    yield
    
    logger.info("Shutting down application...")


app = FastAPI(
    title="Digital Social Score API",
    description="API for detecting text toxicity with GDPR compliance and scalability",
    version="1.0.0",
    lifespan=lifespan
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware for logging and metrics."""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Log request
    logger.info(
        f"path={request.url.path} method={request.method} "
        f"status={response.status_code} duration={duration:.3f}s"
    )
    
    # Record metrics
    REQUEST_COUNT.labels(
        endpoint=request.url.path,
        method=request.method,
        status=response.status_code
    ).inc()
    REQUEST_DURATION.labels(endpoint=request.url.path).observe(duration)
    
    return response


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "service": "Digital Social Score API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    return HealthResponse(
        status="healthy",
        model_loaded=toxicity_detector is not None
    )


@app.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Analyze text for toxicity.
    
    Returns a score from 0 (non-toxic) to 100 (highly toxic).
    Complies with GDPR by not storing personal data.
    """
    try:
        # GDPR compliance: generate anonymized ID
        text_hash = gdpr_handler.anonymize_text(request.text)
        
        # Detect toxicity
        result = toxicity_detector.analyze(request.text)
        
        # Record metric
        TOXICITY_SCORE.observe(result['score'])
        
        logger.info(
            f"Analysis completed - text_hash={text_hash[:16]}... "
            f"score={result['score']:.2f}"
        )
        
        return TextAnalysisResponse(
            text_id=text_hash,
            score=result['score'],
            toxic=result['toxic'],
            categories=result['categories']
        )
        
    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        raise HTTPException(status_code=500, detail="Error analyzing text")


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return JSONResponse(
        content=generate_latest().decode('utf-8'),
        media_type=CONTENT_TYPE_LATEST
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
