from functools import wraps
from flask import request, jsonify, session
import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)

    def is_allowed(self, client_id):
        now = time.time()
        client_requests = self.requests[client_id]

        client_requests = [
            req_time
            for req_time in client_requests
            if req_time > now - self.time_window
        ]
        self.requests[client_id] = client_requests

        if len(client_requests) >= self.max_requests:
            return False

        client_requests.append(now)
        return True

    def limit(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = request.remote_addr
            if session.get("user"):
                client_id = f"user_{session['user']}"

            if not self.is_allowed(client_id):
                return (
                    jsonify({"error": "Rate limit exceeded. Please try again later."}),
                    429,
                )

            return f(*args, **kwargs)

        return decorated_function

rate_limiter = RateLimiter(max_requests=10, time_window=60)
