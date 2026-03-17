"""
Custom HTTP response wrapper for consistent API responses.
"""
from rest_framework.response import Response


class CustomResponse:
    
    def __init__(self, success: bool, message: str, status_code: int, data=None):
        self.data = {
            'success': success,
            'message': message,
        }
        if data is not None:
            self.data['data'] = data
        self.status_code = status_code
    
    def __call__(self):
        """Allow the instance to be called as a response object."""
        return Response(self.data, status=self.status_code)
    
    def __new__(cls, success: bool, message: str, status_code: int, data=None):
        """Return a DRF Response object directly when instantiated."""
        response_data = {
            'success': success,
            'message': message,
        }
        if data is not None:
            response_data['data'] = data
        return Response(response_data, status=status_code)
