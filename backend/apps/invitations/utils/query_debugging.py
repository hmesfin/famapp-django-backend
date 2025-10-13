"""
Query debugging utilities for the invitations app
Provides tools to identify and log slow queries and N+1 problems

Ham Dog & TC's Database Optimization Toolkit:
- Query counting and timing
- N+1 query detection
- Performance logging
- Debug decorators for services
"""

import logging
import functools
from typing import Callable, Any
from django.db import connection
from django.conf import settings


logger = logging.getLogger('invitations.performance')


class QueryCounter:
    """Context manager to count database queries"""
    
    def __init__(self):
        self.initial_count = 0
        self.final_count = 0
    
    def __enter__(self):
        self.initial_count = len(connection.queries)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.final_count = len(connection.queries)
    
    @property
    def query_count(self):
        """Get the number of queries executed"""
        return self.final_count - self.initial_count
    
    def get_queries(self):
        """Get the actual queries that were executed"""
        return connection.queries[self.initial_count:self.final_count]


def log_slow_queries(func: Callable) -> Callable:
    """
    Decorator to log slow database queries
    
    Usage:
        @log_slow_queries
        def my_service_method(self):
            # Your code here
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not settings.DEBUG:
            return func(*args, **kwargs)
            
        with QueryCounter() as counter:
            result = func(*args, **kwargs)
        
        # Log if more than 5 queries or any slow queries
        if counter.query_count > 5:
            logger.warning(
                f"{func.__name__} executed {counter.query_count} queries. "
                f"Potential N+1 problem detected."
            )
        
        # Check for slow queries (>100ms)
        slow_queries = [
            q for q in counter.get_queries() 
            if float(q['time']) > 0.1
        ]
        
        if slow_queries:
            logger.warning(
                f"{func.__name__} has {len(slow_queries)} slow queries "
                f"(>100ms): {[q['sql'][:100] + '...' for q in slow_queries]}"
            )
        
        return result
    return wrapper


def debug_queries(func: Callable) -> Callable:
    """
    Decorator to debug and log all queries for a function
    Only active in DEBUG mode
    
    Usage:
        @debug_queries
        def my_problematic_method(self):
            # Your code here
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not settings.DEBUG:
            return func(*args, **kwargs)
            
        with QueryCounter() as counter:
            result = func(*args, **kwargs)
        
        logger.debug(
            f"{func.__name__} executed {counter.query_count} queries:"
        )
        
        for i, query in enumerate(counter.get_queries(), 1):
            logger.debug(
                f"Query {i}: {query['sql'][:200]}... "
                f"(Time: {query['time']}s)"
            )
        
        return result
    return wrapper


def analyze_queryset_performance(queryset, operation_name: str = "Unknown"):
    """
    Analyze the performance characteristics of a queryset
    
    Args:
        queryset: Django queryset to analyze
        operation_name: Name of the operation for logging
    """
    if not settings.DEBUG:
        return
    
    # Force evaluation and count queries
    with QueryCounter() as counter:
        list(queryset)  # Force evaluation
    
    logger.info(
        f"QuerySet Analysis for {operation_name}:\n"
        f"  - Query Count: {counter.query_count}\n"
        f"  - SQL: {queryset.query}\n"
        f"  - Executed Queries: {len(counter.get_queries())}"
    )
    
    if counter.query_count > 1:
        logger.warning(
            f"Potential N+1 problem in {operation_name}: "
            f"{counter.query_count} queries executed"
        )


class PerformanceProfiler:
    """
    Context manager for profiling database operations
    
    Usage:
        with PerformanceProfiler("invitation_stats_calculation") as profiler:
            # Your database operations here
            stats = calculate_stats()
        
        print(f"Operation took {profiler.query_count} queries")
    """
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.counter = QueryCounter()
    
    def __enter__(self):
        self.counter.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.counter.__exit__(exc_type, exc_val, exc_tb)
        
        if settings.DEBUG:
            self._log_performance()
    
    def _log_performance(self):
        """Log performance metrics"""
        query_count = self.counter.query_count
        queries = self.counter.get_queries()
        
        total_time = sum(float(q['time']) for q in queries)
        
        logger.info(
            f"Performance Profile for {self.operation_name}:\n"
            f"  - Total Queries: {query_count}\n"
            f"  - Total Time: {total_time:.4f}s\n"
            f"  - Average Time per Query: {total_time/max(query_count, 1):.4f}s"
        )
        
        if query_count > 10:
            logger.warning(
                f"High query count detected in {self.operation_name}: "
                f"{query_count} queries"
            )
        
        # Log slowest queries
        slow_queries = sorted(queries, key=lambda q: float(q['time']), reverse=True)[:3]
        if slow_queries:
            logger.info(f"Slowest queries in {self.operation_name}:")
            for i, query in enumerate(slow_queries, 1):
                logger.info(
                    f"  {i}. {query['sql'][:150]}... ({query['time']}s)"
                )
    
    @property
    def query_count(self):
        return self.counter.query_count


def log_queryset_sql(queryset, name: str = "QuerySet"):
    """
    Log the SQL for a queryset without executing it
    
    Args:
        queryset: Django queryset
        name: Name for logging purposes
    """
    if settings.DEBUG:
        logger.debug(f"{name} SQL: {queryset.query}")


# Performance monitoring decorators for specific use cases

def monitor_invitation_queries(func: Callable) -> Callable:
    """
    Specialized decorator for monitoring invitation-related queries
    Provides detailed logging for invitation operations
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not settings.DEBUG:
            return func(*args, **kwargs)
        
        operation_name = f"invitation_{func.__name__}"
        
        with PerformanceProfiler(operation_name) as profiler:
            result = func(*args, **kwargs)
        
        # Specific warnings for invitation operations
        if profiler.query_count > 3:
            logger.warning(
                f"Invitation operation {func.__name__} may have N+1 queries: "
                f"{profiler.query_count} total queries"
            )
        
        return result
    return wrapper


def warn_if_no_select_related(queryset, expected_relations: list = None):
    """
    Warn if a queryset doesn't use select_related for expected relations
    
    Args:
        queryset: Django queryset to check
        expected_relations: List of expected select_related fields
    """
    if not settings.DEBUG or not expected_relations:
        return
    
    select_related_fields = set(queryset.query.select_related or {})
    expected_fields = set(expected_relations)
    
    missing_fields = expected_fields - select_related_fields
    
    if missing_fields:
        logger.warning(
            f"QuerySet may have N+1 problems. Missing select_related for: "
            f"{', '.join(missing_fields)}"
        )