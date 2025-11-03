"""
FastAPI application for Digital Social Score API

Provides endpoints for text toxicity detection with GDPR compliance.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
import time
import logging
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from src.models.toxicity_classifier import get_classifier, analyze_toxicity
from src.utils.anonymizer import TextAnonymizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'api_requests_total', 
    'Total API requests',
    ['endpoint', 'method', 'status']
)
REQUEST_DURATION = Histogram(
    'api_request_duration_seconds',
    'Request duration in seconds',
    ['endpoint']
)
TOXICITY_SCORE_HISTOGRAM = Histogram(
    'toxicity_score',
    'Distribution of toxicity scores',
    buckets=[0, 20, 40, 60, 80, 100]
)

# Initialize FastAPI app
app = FastAPI(
    title="Digital Social Score API",
    description="GDPR-compliant text toxicity detection API with scoring from 0 to 100",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components (lazy loading)
anonymizer = None
classifier = None


def get_anonymizer():
    """Get or create the global anonymizer instance."""
    global anonymizer
    if anonymizer is None:
        try:
            anonymizer = TextAnonymizer()
            logger.info("Anonymizer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize anonymizer: {e}")
            anonymizer = None
    return anonymizer


def get_toxicity_classifier():
    """Get or create the global classifier instance."""
    global classifier
    if classifier is None:
        try:
            classifier = get_classifier()
            logger.info("Toxicity classifier initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize classifier: {e}")
            classifier = None
    return classifier


# Request/Response Models
class TextAnalysisRequest(BaseModel):
    """Request model for text analysis."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to analyze")
    anonymize: bool = Field(default=True, description="Whether to anonymize PII before analysis")
    anonymization_method: str = Field(default="mask", description="Anonymization method: mask, pseudonymize, or remove")
    
    @validator('anonymization_method')
    def validate_method(cls, v):
        if v not in ['mask', 'pseudonymize', 'remove']:
            raise ValueError('anonymization_method must be one of: mask, pseudonymize, remove')
        return v


class BatchTextAnalysisRequest(BaseModel):
    """Request model for batch text analysis."""
    texts: List[str] = Field(..., min_items=1, max_items=100, description="List of texts to analyze")
    anonymize: bool = Field(default=True, description="Whether to anonymize PII before analysis")
    anonymization_method: str = Field(default="mask", description="Anonymization method: mask, pseudonymize, or remove")


class ToxicityResponse(BaseModel):
    """Response model for toxicity analysis."""
    toxicity_score: float = Field(..., ge=0, le=100, description="Toxicity score from 0 to 100")
    is_toxic: bool = Field(..., description="Whether the text is considered toxic")
    confidence: float = Field(..., description="Confidence level of the prediction")
    severity: str = Field(..., description="Severity level: none, low, medium, high, critical")
    categories: Dict[str, float] = Field(..., description="Scores for specific toxicity categories")
    anonymized: bool = Field(..., description="Whether the text was anonymized")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: float
    services: Dict[str, str]


# Middleware for request logging and metrics
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and collect metrics."""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Record metrics
    REQUEST_COUNT.labels(
        endpoint=request.url.path,
        method=request.method,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        endpoint=request.url.path
    ).observe(duration)
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s"
    )
    
    return response


# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Digital Social Score API",
        "version": "1.0.0",
        "description": "GDPR-compliant text toxicity detection API",
        "documentation": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    anon = get_anonymizer()
    clf = get_toxicity_classifier()
    
    return HealthResponse(
        status="healthy" if (anon and clf) else "degraded",
        timestamp=time.time(),
        services={
            "anonymizer": "ready" if anon else "unavailable",
            "classifier": "ready" if clf else "unavailable"
        }
    )


@app.post("/analyze", response_model=ToxicityResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Analyze text for toxicity.
    
    This endpoint:
    1. Optionally anonymizes the text (GDPR compliance)
    2. Analyzes toxicity using ML model
    3. Returns toxicity score (0-100) and detailed analysis
    """
    start_time = time.time()
    
    text_to_analyze = request.text
    was_anonymized = False
    
    try:
        # Step 1: Anonymize if requested
        if request.anonymize:
            anon = get_anonymizer()
            if anon:
                text_to_analyze, _ = anon.anonymize(
                    request.text, 
                    method=request.anonymization_method
                )
                was_anonymized = True
                logger.info("Text anonymized before analysis")
            else:
                logger.warning("Anonymizer not available, proceeding without anonymization")
        
        # Step 2: Analyze toxicity
        clf = get_toxicity_classifier()
        if not clf:
            raise HTTPException(
                status_code=503,
                detail="Toxicity classifier not available"
            )
        
        result = clf.predict(text_to_analyze)
        
        # Record toxicity score metric
        TOXICITY_SCORE_HISTOGRAM.observe(result["toxicity_score"])
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        return ToxicityResponse(
            toxicity_score=result["toxicity_score"],
            is_toxic=result["is_toxic"],
            confidence=result["confidence"],
            severity=result["severity"],
            categories=result["categories"],
            anonymized=was_anonymized,
            processing_time_ms=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing text: {str(e)}"
        )


@app.post("/analyze/batch")
async def analyze_batch(request: BatchTextAnalysisRequest):
    """
    Analyze multiple texts for toxicity in batch.
    
    Returns a list of toxicity analysis results.
    """
    start_time = time.time()
    
    try:
        results = []
        
        for text in request.texts:
            text_request = TextAnalysisRequest(
                text=text,
                anonymize=request.anonymize,
                anonymization_method=request.anonymization_method
            )
            result = await analyze_text(text_request)
            results.append(result.dict())
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "results": results,
            "count": len(results),
            "total_processing_time_ms": round(processing_time, 2)
        }
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch analysis: {str(e)}"
        )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/gdpr/compliance")
async def gdpr_compliance():
    """
    GDPR compliance information endpoint.
    
    Explains how the API handles personal data.
    """
    return {
        "compliant": True,
        "data_processing": {
            "personal_data_storage": "None - No personal data is stored",
            "anonymization": "PII is anonymized using NER before processing",
            "data_retention": "No data is retained after request processing",
            "user_rights": [
                "Right to access: No personal data is collected",
                "Right to erasure: N/A - No data stored",
                "Right to data portability: N/A - No data stored"
            ]
        },
        "security_measures": [
            "PII anonymization using spaCy NER",
            "No logging of sensitive data",
            "Secure API endpoints",
            "Rate limiting (recommended in production)"
        ],
        "anonymization_methods": [
            "mask: Replace PII with [ENTITY_TYPE]",
            "pseudonymize: Replace with consistent hash-based identifier",
            "remove: Remove PII completely"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
