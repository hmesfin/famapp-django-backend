"""
Management command to analyze invitation query performance
Identifies potential N+1 queries and optimization opportunities

Usage:
    python manage.py analyze_invitation_queries
    python manage.py analyze_invitation_queries --verbose
    python manage.py analyze_invitation_queries --test-data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection

from apps.invitations.models import Invitation
from apps.invitations.services import InvitationStatsService, InvitationService
from apps.invitations.api.views import InvitationViewSet
from apps.invitations.utils.query_debugging import QueryCounter, PerformanceProfiler

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Analyze invitation query performance and identify optimization opportunities"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed query information",
        )
        parser.add_argument(
            "--test-data",
            action="store_true",
            help="Create test data for analysis",
        )

    def handle(self, *args, **options):
        self.verbose = options["verbose"]

        if options["test_data"]:
            self.create_test_data()

        self.stdout.write(
            self.style.SUCCESS("Starting invitation query performance analysis...\n")
        )

        # Test various query patterns
        self.analyze_basic_queries()
        self.analyze_stats_queries()
        self.analyze_viewset_queries()
        self.analyze_admin_queries()

        self.stdout.write(self.style.SUCCESS("\nQuery performance analysis completed!"))

    def create_test_data(self):
        """Create test data for analysis if none exists"""
        if Invitation.objects.count() < 10:
            self.stdout.write("Creating test data...")

            # Create test users if needed
            admin_user, _ = User.objects.get_or_create(
                email="admin@test.com",
                defaults={"first_name": "Admin", "last_name": "User"},
            )

            # Create test invitations
            for i in range(20):
                Invitation.objects.get_or_create(
                    email=f"test{i}@example.com",
                    defaults={
                        "first_name": f"Test{i}",
                        "last_name": "User",
                        "invited_by": admin_user,
                        "role": "member" if i % 2 == 0 else "admin",
                        "status": "pending" if i % 3 == 0 else "accepted",
                    },
                )

            self.stdout.write(self.style.SUCCESS("Test data created.\n"))

    def analyze_basic_queries(self):
        """Analyze basic invitation queries"""
        self.stdout.write(self.style.WARNING("=== Basic Query Analysis ==="))

        # Test basic listing
        with PerformanceProfiler("basic_invitation_list") as profiler:
            invitations = list(Invitation.objects.active()[:10])

        self.report_performance("Basic Invitation List", profiler)

        # Test with select_related
        with PerformanceProfiler("optimized_invitation_list") as profiler:
            invitations = list(
                Invitation.objects.active().select_related("invited_by", "accepted_by")[
                    :10
                ]
            )

        self.report_performance(
            "Optimized Invitation List (with select_related)", profiler
        )

    def analyze_stats_queries(self):
        """Analyze stats service queries"""
        self.stdout.write(self.style.WARNING("\n=== Stats Service Analysis ==="))

        if not User.objects.exists():
            self.stdout.write("No users found for stats analysis")
            return

        user = User.objects.first()
        stats_service = InvitationStatsService()

        # Test stats calculation
        with PerformanceProfiler("stats_calculation") as profiler:
            stats = stats_service.calculate_stats(user)

        self.report_performance("Stats Calculation", profiler)

        if self.verbose:
            self.stdout.write(f"Stats result: {stats}")

        # Test user stats
        with PerformanceProfiler("user_invitation_stats") as profiler:
            user_stats = stats_service.get_user_invitation_stats(user)

        self.report_performance("User Invitation Stats", profiler)

    def analyze_viewset_queries(self):
        """Analyze ViewSet query patterns"""
        self.stdout.write(self.style.WARNING("\n=== ViewSet Query Analysis ==="))

        if not User.objects.exists():
            self.stdout.write("No users found for viewset analysis")
            return

        # Simulate ViewSet queryset
        user = User.objects.first()

        # Test unoptimized queryset (what it was before)
        with PerformanceProfiler("unoptimized_viewset_queryset") as profiler:
            old_queryset = Invitation.objects.active().order_by("-created_at")[:10]
            # Simulate accessing foreign key fields
            for invitation in old_queryset:
                _ = invitation.invited_by.email if invitation.invited_by else None

        self.report_performance("Unoptimized ViewSet Queryset", profiler)

        # Test optimized queryset (current implementation)
        with PerformanceProfiler("optimized_viewset_queryset") as profiler:
            new_queryset = (
                Invitation.objects.active()
                .select_related("invited_by", "accepted_by", "created_by", "updated_by")
                .order_by("-created_at")[:10]
            )
            # Simulate accessing foreign key fields
            for invitation in new_queryset:
                _ = invitation.invited_by.email if invitation.invited_by else None

        self.report_performance("Optimized ViewSet Queryset", profiler)

    def analyze_admin_queries(self):
        """Analyze admin interface queries"""
        self.stdout.write(self.style.WARNING("\n=== Admin Interface Analysis ==="))

        # Test admin queryset
        with PerformanceProfiler("admin_queryset") as profiler:
            admin_queryset = Invitation.objects.select_related(
                "invited_by", "accepted_by", "created_by", "updated_by", "deleted_by"
            ).order_by("-created_at")[:10]
            list(admin_queryset)

        self.report_performance("Admin Interface Queryset", profiler)

    def report_performance(self, operation_name: str, profiler: PerformanceProfiler):
        """Report performance metrics for an operation"""
        query_count = profiler.query_count

        if query_count <= 3:
            style = self.style.SUCCESS
            status = "EXCELLENT"
        elif query_count <= 5:
            style = self.style.WARNING
            status = "GOOD"
        else:
            style = self.style.ERROR
            status = "NEEDS_OPTIMIZATION"

        self.stdout.write(style(f"{operation_name}: {query_count} queries [{status}]"))

        if self.verbose and query_count > 1:
            queries = profiler.counter.get_queries()
            for i, query in enumerate(queries, 1):
                self.stdout.write(
                    f"  Query {i}: {query['sql'][:100]}... ({query['time']}s)"
                )

    def analyze_query_plans(self):
        """Analyze query execution plans (PostgreSQL specific)"""
        if "postgresql" not in connection.settings_dict["ENGINE"]:
            self.stdout.write("Query plan analysis only available for PostgreSQL")
            return

        self.stdout.write(self.style.WARNING("\n=== Query Plan Analysis ==="))

        # Analyze key queries
        queries_to_analyze = [
            "SELECT * FROM invitations_invitation WHERE is_deleted = false ORDER BY created_at DESC LIMIT 10",
            "SELECT * FROM invitations_invitation WHERE email = %s AND status = 'pending' AND is_deleted = false",
            "SELECT COUNT(*) FROM invitations_invitation WHERE status = 'pending' AND is_deleted = false",
        ]

        with connection.cursor() as cursor:
            for sql in queries_to_analyze:
                try:
                    cursor.execute(f"EXPLAIN ANALYZE {sql}", ["test@example.com"])
                    plan = cursor.fetchall()

                    self.stdout.write(f"\nQuery: {sql[:60]}...")
                    for row in plan:
                        self.stdout.write(f"  {row[0]}")
                except Exception as e:
                    self.stdout.write(f"Error analyzing query: {e}")
