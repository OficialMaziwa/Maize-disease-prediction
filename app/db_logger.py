import json
from datetime import datetime
from flask import request, session
from app.user_db import user_db


class DatabaseLogger:
    """Database logging system for persistent storage of all events"""

    def __init__(self):
        self.connection = None

    def _get_connection(self):
        """Get database connection"""
        if not user_db.connection or not user_db.connection.is_connected():
            user_db.connect()
        return user_db.connection

    def _get_client_ip(self):
        """Get client IP address"""
        if request:
            if request.headers.get("X-Forwarded-For"):
                return request.headers.get("X-Forwarded-For").split(",")[0]
            if request.headers.get("X-Real-IP"):
                return request.headers.get("X-Real-IP")
            return request.remote_addr
        return "N/A"

    def _get_user_agent(self):
        """Get user agent"""
        if request and hasattr(request, "user_agent"):
            return request.user_agent.string if request.user_agent else "Unknown"
        return "N/A"

    def log_security_event(
        self, event_type, details, severity="INFO", user_id=None, user_role=None
    ):
        """Log security event to database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO security_logs 
                (event_type, severity, details, ip_address, user_agent, user_id, user_role, endpoint, method, url, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
                (
                    event_type,
                    severity,
                    str(details)[:1000],
                    self._get_client_ip(),
                    self._get_user_agent(),
                    user_id or session.get("user_id"),
                    user_role or session.get("user_role"),
                    request.endpoint if request else None,
                    request.method if request else None,
                    request.url if request else None,
                ),
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Database logging error: {e}")
            return False

    def log_auth_event(self, event_type, username, success, details=None, user_id=None):
        """Log authentication event to database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO auth_logs 
                (event_type, username, success, details, ip_address, user_agent, user_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """,
                (
                    event_type,
                    username,
                    1 if success else 0,
                    str(details)[:500] if details else None,
                    self._get_client_ip(),
                    self._get_user_agent(),
                    user_id or session.get("user_id"),
                ),
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Auth logging error: {e}")
            return False

    def log_access(self, status_code, response_time_ms=0):
        """Log HTTP access to database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO access_logs 
                (ip_address, method, endpoint, url, status_code, response_time_ms, user_agent, user_id, user_role, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
                (
                    self._get_client_ip(),
                    request.method if request else None,
                    request.endpoint if request else None,
                    request.url if request else None,
                    status_code,
                    response_time_ms,
                    self._get_user_agent(),
                    session.get("user_id"),
                    session.get("user_role"),
                ),
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Access logging error: {e}")
            return False

    def log_attack(
        self,
        attack_type,
        pattern_matched,
        request_data=None,
        severity="MEDIUM",
        blocked=False,
    ):
        """Log detected attack to database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO attack_logs 
                (attack_type, pattern_matched, ip_address, user_agent, endpoint, method, url, request_data, severity, blocked, user_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
                (
                    attack_type,
                    pattern_matched[:500] if pattern_matched else None,
                    self._get_client_ip(),
                    self._get_user_agent(),
                    request.endpoint if request else None,
                    request.method if request else None,
                    request.url if request else None,
                    str(request_data)[:1000] if request_data else None,
                    severity,
                    1 if blocked else 0,
                    session.get("user_id"),
                ),
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Attack logging error: {e}")
            return False

    def log_db_operation(
        self, operation, table, query, parameters=None, duration_ms=None
    ):
        """Log database operation to database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO db_operation_logs 
                (operation_type, table_name, query, parameters, duration_ms, ip_address, user_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """,
                (
                    operation,
                    table,
                    query[:500] if query else None,
                    str(parameters)[:500] if parameters else None,
                    duration_ms,
                    self._get_client_ip(),
                    session.get("user_id"),
                ),
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"DB operation logging error: {e}")
            return False

    def log_api_call(
        self, api_name, request_data=None, response_data=None, duration_ms=None
    ):
        """Log API call to database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO api_logs 
                (api_name, request_data, response_data, duration_ms, ip_address, user_id, user_role, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """,
                (
                    api_name,
                    json.dumps(request_data)[:1000] if request_data else None,
                    json.dumps(response_data)[:1000] if response_data else None,
                    duration_ms,
                    self._get_client_ip(),
                    session.get("user_id"),
                    session.get("user_role"),
                ),
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"API logging error: {e}")
            return False

    def log_system_health(self, health_type, status, message, details=None):
        """Log system health status to database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO system_health_logs 
                (health_type, status, message, details, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """,
                (
                    health_type,
                    status,
                    message,
                    json.dumps(details) if details else None,
                ),
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Health logging error: {e}")
            return False

    def get_security_logs(self, limit=100, offset=0, event_type=None, severity=None):
        """Retrieve security logs from database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM security_logs WHERE 1=1"
            params = []

            if event_type:
                query += " AND event_type = %s"
                params.append(event_type)
            if severity:
                query += " AND severity = %s"
                params.append(severity)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(query, params)
            results = cursor.fetchall()

            for result in results:
                if result.get("created_at"):
                    result["created_at"] = result["created_at"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

            cursor.close()
            return results
        except Exception as e:
            print(f"Error retrieving security logs: {e}")
            return []

    def get_auth_logs(self, limit=100, offset=0, success=None):
        """Retrieve authentication logs from database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM auth_logs WHERE 1=1"
            params = []

            if success is not None:
                query += " AND success = %s"
                params.append(1 if success else 0)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(query, params)
            results = cursor.fetchall()

            for result in results:
                if result.get("created_at"):
                    result["created_at"] = result["created_at"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

            cursor.close()
            return results
        except Exception as e:
            print(f"Error retrieving auth logs: {e}")
            return []

    def get_attack_logs(self, limit=100, offset=0, severity=None):
        """Retrieve attack logs from database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM attack_logs WHERE 1=1"
            params = []

            if severity:
                query += " AND severity = %s"
                params.append(severity)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(query, params)
            results = cursor.fetchall()

            for result in results:
                if result.get("created_at"):
                    result["created_at"] = result["created_at"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

            cursor.close()
            return results
        except Exception as e:
            print(f"Error retrieving attack logs: {e}")
            return []

    def get_stats(self, hours=24):
        """Get log statistics for dashboard"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT 
                    (SELECT COUNT(*) FROM security_logs WHERE created_at > DATE_SUB(NOW(), INTERVAL %s HOUR)) as total_security,
                    (SELECT COUNT(*) FROM auth_logs WHERE created_at > DATE_SUB(NOW(), INTERVAL %s HOUR) AND success = 1) as success_logins,
                    (SELECT COUNT(*) FROM auth_logs WHERE created_at > DATE_SUB(NOW(), INTERVAL %s HOUR) AND success = 0) as failed_logins,
                    (SELECT COUNT(*) FROM attack_logs WHERE created_at > DATE_SUB(NOW(), INTERVAL %s HOUR)) as total_attacks,
                    (SELECT COUNT(*) FROM access_logs WHERE created_at > DATE_SUB(NOW(), INTERVAL %s HOUR) AND status_code >= 400) as error_requests
            """,
                (hours, hours, hours, hours, hours),
            )

            stats = cursor.fetchone()
            cursor.close()
            return stats or {
                "total_security": 0,
                "success_logins": 0,
                "failed_logins": 0,
                "total_attacks": 0,
                "error_requests": 0,
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                "total_security": 0,
                "success_logins": 0,
                "failed_logins": 0,
                "total_attacks": 0,
                "error_requests": 0,
            }


db_logger = DatabaseLogger()
