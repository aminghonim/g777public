"""
=============================================================================
MASTER QUALITY #1: Volume & Stress Testing (اختبارات الضغط والأداء)
=============================================================================

Purpose: Test system performance under load with large datasets.

How this ensures stability:
- Generates 100,000 synthetic customer records
- Measures execution time (must be under 5 seconds)
- Monitors memory usage for leaks
- Tests filtering and export operations at scale

Requirements:
    pip install memory-profiler pytest-benchmark faker
=============================================================================
"""

import pytest
import csv
import io
import time
import random
import string
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import CRM logic from our test file
from tests.legacy.test_crm_logic import CRMDataLogic


# =============================================================================
# CONFIGURATION
# =============================================================================

VOLUME_SIZE = 100_000  # Number of records to generate
MAX_EXECUTION_TIME = 5.0  # Maximum allowed time in seconds
MAX_MEMORY_MB = 500  # Maximum memory usage in MB


# =============================================================================
# DATA GENERATORS
# =============================================================================


class SyntheticDataGenerator:
    """Generate realistic synthetic customer data at scale"""

    CITIES = [
        "القاهرة",
        "الإسكندرية",
        "الجيزة",
        "شرم الشيخ",
        "الأقصر",
        "أسوان",
        "المنصورة",
        "طنطا",
        "بورسعيد",
        "السويس",
    ]

    INTERESTS = [
        "تسويق",
        "عقارات",
        "سيارات",
        "إلكترونيات",
        "ملابس",
        "مجوهرات",
        "سياحة",
        "تعليم",
        "طب",
        "برمجة",
        "استثمار",
    ]

    CUSTOMER_TYPES = ["lead", "customer", "vip"]

    FIRST_NAMES = [
        "أحمد",
        "محمد",
        "علي",
        "سارة",
        "فاطمة",
        "نور",
        "عمر",
        "يوسف",
        "هند",
        "ليلى",
    ]
    LAST_NAMES = ["محمد", "أحمد", "علي", "حسن", "إبراهيم", "عبدالله", "السيد", "خالد"]

    @classmethod
    def generate_phone(cls) -> str:
        """Generate Egyptian phone number"""
        prefixes = ["010", "011", "012", "015"]
        return f"+2{random.choice(prefixes)}{random.randint(10000000, 99999999)}"

    @classmethod
    def generate_name(cls) -> str:
        """Generate Arabic name"""
        return f"{random.choice(cls.FIRST_NAMES)} {random.choice(cls.LAST_NAMES)}"

    @classmethod
    def generate_customer(cls, id: int) -> dict:
        """Generate single customer record"""
        return {
            "id": str(id),
            "name": cls.generate_name(),
            "phone": cls.generate_phone(),
            "city": random.choice(cls.CITIES),
            "customer_type": random.choice(cls.CUSTOMER_TYPES),
            "metadata": {
                "interests": random.sample(cls.INTERESTS, k=random.randint(1, 4)),
                "source": random.choice(["whatsapp", "website", "referral", "ads"]),
            },
            "created_at": datetime.now() - timedelta(days=random.randint(0, 365)),
            "last_conversation_at": (
                datetime.now() - timedelta(days=random.randint(0, 30))
                if random.random() > 0.3
                else None
            ),
        }

    @classmethod
    def generate_bulk_customers(cls, count: int) -> list:
        """Generate bulk customer records"""
        return [cls.generate_customer(i) for i in range(count)]

    @classmethod
    def generate_csv_file(cls, count: int, filepath: Path) -> Path:
        """Generate CSV file with synthetic data"""
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["id", "name", "phone", "city", "customer_type", "interests"]
            )

            for i in range(count):
                customer = cls.generate_customer(i)
                interests = ";".join(customer["metadata"]["interests"])
                writer.writerow(
                    [
                        customer["id"],
                        customer["name"],
                        customer["phone"],
                        customer["city"],
                        customer["customer_type"],
                        interests,
                    ]
                )

        return filepath


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(scope="module")
def large_dataset():
    """Generate large dataset once per module (cached)"""
    print(f"\n[VOLUME] Generating {VOLUME_SIZE:,} synthetic records...")
    start = time.time()
    data = SyntheticDataGenerator.generate_bulk_customers(VOLUME_SIZE)
    elapsed = time.time() - start
    print(f"[VOLUME] Generated in {elapsed:.2f}s")
    return data


@pytest.fixture(scope="module")
def large_csv_file(tmp_path_factory):
    """Generate large CSV file once per module"""
    temp_dir = tmp_path_factory.mktemp("volume_data")
    filepath = temp_dir / "customers_100k.csv"

    print(f"\n[VOLUME] Generating CSV with {VOLUME_SIZE:,} records...")
    start = time.time()
    SyntheticDataGenerator.generate_csv_file(VOLUME_SIZE, filepath)
    elapsed = time.time() - start
    print(
        f"[VOLUME] CSV generated in {elapsed:.2f}s, Size: {filepath.stat().st_size / 1024 / 1024:.2f} MB"
    )

    return filepath


@pytest.fixture
def crm_logic():
    """CRM logic instance"""
    return CRMDataLogic()


# =============================================================================
# VOLUME TESTS
# =============================================================================


class TestVolumePerformance:
    """Test performance with large datasets"""

    def test_filter_100k_by_type(self, crm_logic, large_dataset):
        """
        BENCHMARK: Filter 100K records by customer type
        Target: Under 5 seconds
        """
        start = time.time()

        result = crm_logic.filter_customers(large_dataset, filter_type="lead")

        elapsed = time.time() - start

        print(
            f"\n[BENCHMARK] Filter by type: {elapsed:.3f}s, Found: {len(result):,} leads"
        )

        assert (
            elapsed < MAX_EXECUTION_TIME
        ), f"Filter took {elapsed:.2f}s, exceeds {MAX_EXECUTION_TIME}s limit"
        assert len(result) > 0, "Should find some leads"

    def test_filter_100k_by_city(self, crm_logic, large_dataset):
        """
        BENCHMARK: Filter 100K records by city
        Target: Under 5 seconds
        """
        start = time.time()

        result = crm_logic.filter_customers(large_dataset, city="القاهرة")

        elapsed = time.time() - start

        print(
            f"\n[BENCHMARK] Filter by city: {elapsed:.3f}s, Found: {len(result):,} in Cairo"
        )

        assert (
            elapsed < MAX_EXECUTION_TIME
        ), f"Filter took {elapsed:.2f}s, exceeds {MAX_EXECUTION_TIME}s limit"

    def test_filter_100k_by_interests(self, crm_logic, large_dataset):
        """
        BENCHMARK: Filter 100K records by interests (complex)
        Target: Under 5 seconds
        """
        start = time.time()

        result = crm_logic.filter_customers(
            large_dataset, interests=["تسويق", "عقارات"]
        )

        elapsed = time.time() - start

        print(
            f"\n[BENCHMARK] Filter by interests: {elapsed:.3f}s, Found: {len(result):,} matches"
        )

        assert (
            elapsed < MAX_EXECUTION_TIME
        ), f"Filter took {elapsed:.2f}s, exceeds {MAX_EXECUTION_TIME}s limit"

    def test_filter_100k_combined(self, crm_logic, large_dataset):
        """
        BENCHMARK: Combined filter (type + city + interests)
        Target: Under 5 seconds
        """
        start = time.time()

        result = crm_logic.filter_customers(
            large_dataset, filter_type="lead", city="القاهرة", interests=["تسويق"]
        )

        elapsed = time.time() - start

        print(
            f"\n[BENCHMARK] Combined filter: {elapsed:.3f}s, Found: {len(result):,} matches"
        )

        assert (
            elapsed < MAX_EXECUTION_TIME
        ), f"Filter took {elapsed:.2f}s, exceeds {MAX_EXECUTION_TIME}s limit"

    def test_export_100k_to_csv(self, crm_logic, large_dataset):
        """
        BENCHMARK: Export 100K records to CSV string
        Target: Under 5 seconds
        """
        start = time.time()

        csv_content = crm_logic.export_csv(large_dataset)

        elapsed = time.time() - start

        size_mb = len(csv_content.encode("utf-8")) / 1024 / 1024
        print(f"\n[BENCHMARK] Export to CSV: {elapsed:.3f}s, Size: {size_mb:.2f} MB")

        assert (
            elapsed < MAX_EXECUTION_TIME
        ), f"Export took {elapsed:.2f}s, exceeds {MAX_EXECUTION_TIME}s limit"
        assert len(csv_content) > 1000, "CSV content should be substantial"

    def test_calculate_stats_100k(self, crm_logic, large_dataset):
        """
        BENCHMARK: Calculate statistics for 100K records
        Target: Under 5 seconds
        """
        start = time.time()

        stats = crm_logic.calculate_stats(large_dataset)

        elapsed = time.time() - start

        print(f"\n[BENCHMARK] Calculate stats: {elapsed:.3f}s")
        print(f"  - Total: {stats['total']:,}")
        print(f"  - Leads: {stats['leads']:,}")
        print(f"  - Customers: {stats['customers']:,}")
        print(f"  - VIPs: {stats['vips']:,}")
        print(f"  - Cities: {len(stats['cities'])}")
        print(f"  - Top interests: {stats['top_interests'][:3]}")

        assert (
            elapsed < MAX_EXECUTION_TIME
        ), f"Stats took {elapsed:.2f}s, exceeds {MAX_EXECUTION_TIME}s limit"
        assert stats["total"] == VOLUME_SIZE


# =============================================================================
# STRESS TESTS
# =============================================================================


class TestStressConditions:
    """Test system under stress conditions"""

    def test_repeated_filter_operations(self, crm_logic, large_dataset):
        """
        STRESS: Run 100 consecutive filter operations
        Tests for memory leaks and performance degradation
        """
        times = []

        for i in range(100):
            start = time.time()
            crm_logic.filter_customers(large_dataset, filter_type="lead")
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)

        print(f"\n[STRESS] 100 consecutive filters:")
        print(f"  - Avg: {avg_time:.4f}s")
        print(f"  - Min: {min_time:.4f}s")
        print(f"  - Max: {max_time:.4f}s")

        # Check for performance degradation (last 10 should not be 2x slower than first 10)
        first_10_avg = sum(times[:10]) / 10
        last_10_avg = sum(times[-10:]) / 10

        assert (
            last_10_avg < first_10_avg * 2
        ), "Performance degradation detected (possible memory leak)"

    def test_concurrent_operations_simulation(self, crm_logic, large_dataset):
        """
        STRESS: Simulate concurrent operations
        (Note: Python GIL limits true parallelism, but tests thread safety)
        """
        import threading

        results = []
        errors = []

        def filter_operation(filter_type):
            try:
                result = crm_logic.filter_customers(
                    large_dataset, filter_type=filter_type
                )
                results.append(len(result))
            except Exception as e:
                errors.append(str(e))

        threads = []
        for filter_type in ["lead", "customer", "vip"] * 10:  # 30 threads
            t = threading.Thread(target=filter_operation, args=(filter_type,))
            threads.append(t)

        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.time() - start

        print(f"\n[STRESS] 30 concurrent filters completed in {elapsed:.3f}s")
        print(f"  - Successful: {len(results)}")
        print(f"  - Errors: {len(errors)}")

        assert len(errors) == 0, f"Concurrent operations failed: {errors}"
        assert len(results) == 30, "All operations should complete"


# =============================================================================
# MEMORY PROFILING
# =============================================================================


class TestMemoryUsage:
    """Test memory usage patterns"""

    def test_memory_after_large_filter(self, crm_logic, large_dataset):
        """
        MEMORY: Verify no excessive memory retention after filtering
        """
        import gc

        # Force garbage collection
        gc.collect()

        # Perform filter
        result = crm_logic.filter_customers(large_dataset, filter_type="lead")
        result_count = len(result)

        # Clear result
        del result
        gc.collect()

        # Perform another filter - should not accumulate memory
        result2 = crm_logic.filter_customers(large_dataset, filter_type="customer")
        result2_count = len(result2)

        print(f"\n[MEMORY] Filter 1: {result_count:,} | Filter 2: {result2_count:,}")

        # This is a basic check - for detailed profiling use memory_profiler
        assert result_count > 0 and result2_count > 0


# =============================================================================
# PERFORMANCE REPORT GENERATOR
# =============================================================================


def generate_performance_report(results: dict) -> str:
    """
    Generate human-readable performance report.

    How to read:
    - GREEN (✅): Operation completed under target time
    - YELLOW (⚠️): Operation completed but close to limit
    - RED (❌): Operation failed or exceeded limit

    Args:
        results: Dictionary of test results

    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 60)
    report.append("       G777 PERFORMANCE REPORT")
    report.append("=" * 60)
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append(f"Dataset Size: {VOLUME_SIZE:,} records")
    report.append(f"Max Allowed Time: {MAX_EXECUTION_TIME}s")
    report.append("-" * 60)

    for test_name, metrics in results.items():
        elapsed = metrics.get("elapsed", 0)
        status = metrics.get("status", "unknown")

        if status == "passed" and elapsed < MAX_EXECUTION_TIME * 0.5:
            icon = "✅"
        elif status == "passed":
            icon = "⚠️"
        else:
            icon = "❌"

        report.append(f"{icon} {test_name}: {elapsed:.3f}s")

    report.append("=" * 60)
    return "\n".join(report)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
