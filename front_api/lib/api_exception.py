from fastapi import Request
from fastapi.responses import JSONResponse

class InsufficientPrivilege(Exception):
    def __init__(self, name: str, date: str):
        self.name = name
        self.date = date

def InsufficientPrivilegeHandler(request: Request, exception: InsufficientPrivilege):
    return JSONResponse(
        status_code=403,
        content={
            'url': str(request.url),
            'name': exception.name,
            'message': 'Insufficient role''s privilege. Please ask for it to admin.',
            'date': exception.date
        }
    )
