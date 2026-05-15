from fastapi import HTTPException, status


class DocumentumError(Exception):
    """Base application error."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(DocumentumError):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found.", code="NOT_FOUND")


class UnauthorizedError(DocumentumError):
    def __init__(self, message: str = "Authentication required."):
        super().__init__(message, code="UNAUTHORIZED")


class ForbiddenError(DocumentumError):
    def __init__(self, message: str = "You don't have permission to do that."):
        super().__init__(message, code="FORBIDDEN")


class ValidationError(DocumentumError):
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")


class FileTooLargeError(DocumentumError):
    def __init__(self, max_mb: int):
        super().__init__(
            f"File exceeds the {max_mb}MB limit.", code="FILE_TOO_LARGE"
        )


class UnsupportedFileTypeError(DocumentumError):
    def __init__(self, ext: str, allowed: list):
        super().__init__(
            f"'.{ext}' is not supported. Allowed: {', '.join(allowed)}.",
            code="UNSUPPORTED_FILE_TYPE",
        )


class ProcessingError(DocumentumError):
    def __init__(self, message: str = "Document processing failed."):
        super().__init__(message, code="PROCESSING_ERROR")


class RateLimitError(DocumentumError):
    def __init__(self):
        super().__init__("Rate limit exceeded. Please slow down.", code="RATE_LIMIT")


# ── HTTP exception helpers ────────────────────────────────────────────────────

def http_404(detail: str = "Not found") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def http_401(detail: str = "Not authenticated") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def http_403(detail: str = "Forbidden") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def http_400(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def http_429() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Rate limit exceeded. Please slow down.",
    )
