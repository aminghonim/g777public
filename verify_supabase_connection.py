#!/usr/bin/env python3
"""
Verify Supabase Connection Log - CNS Task W-04
Implements Smart Retry and connection verification
"""
import os
import sys
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.db_service import get_connection_pool, get_db_cursor
import psycopg2
from psycopg2.extras import RealDictCursor
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.antigravity/supabase_connection_log.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

class SupabaseConnectionVerifier:
    """CNS-compliant Supabase connection verification with Smart Retry"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.connection_pool = None
        self.test_results = {}
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.DatabaseError))
    )
    def get_connection_with_retry(self) -> psycopg2.extensions.connection:
        """Smart Retry connection implementation"""
        logger.info("Attempting Supabase connection with Smart Retry...")
        
        if not self.database_url:
            raise ValueError("DATABASE_URL not found in environment")
            
        conn = psycopg2.connect(
            self.database_url,
            connect_timeout=10,
            application_name="cns_connection_verifier"
        )
        
        logger.info("✅ Supabase connection established successfully")
        return conn
    
    def verify_connection_health(self) -> Dict[str, Any]:
        """Comprehensive connection health check"""
        logger.info("🔍 Starting CNS Supabase Connection Verification...")
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "database_url_configured": bool(self.database_url),
            "connection_pool_status": None,
            "basic_connectivity": False,
            "query_performance": {},
            "table_access": {},
            "error_log": [],
            "recommendations": []
        }
        
        try:
            # Test 1: Connection Pool Status
            logger.info("📊 Testing connection pool...")
            self.connection_pool = get_connection_pool()
            health_report["connection_pool_status"] = {
                "available": self.connection_pool is not None,
                "min_connections": 1 if self.connection_pool else 0,
                "max_connections": 10 if self.connection_pool else 0
            }
            
            # Test 2: Direct Connection with Smart Retry
            logger.info("🔌 Testing direct connection...")
            start_time = time.time()
            conn = self.get_connection_with_retry()
            connection_time = time.time() - start_time
            
            health_report["basic_connectivity"] = True
            health_report["query_performance"]["connection_time_ms"] = round(connection_time * 1000, 2)
            
            if connection_time > 2.0:
                health_report["recommendations"].append("⚠️ Connection time > 2s - consider network optimization")
            
            # Test 3: Query Performance
            logger.info("⚡ Testing query performance...")
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Simple count query
                start_time = time.time()
                cur.execute("SELECT 1 as test")
                cur.fetchone()
                simple_query_time = time.time() - start_time
                health_report["query_performance"]["simple_query_ms"] = round(simple_query_time * 1000, 2)
                
                # Table count query
                start_time = time.time()
                cur.execute("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                result = cur.fetchone()
                table_count_time = time.time() - start_time
                health_report["query_performance"]["table_count_query_ms"] = round(table_count_time * 1000, 2)
                health_report["table_access"]["public_tables_count"] = result['count']
                
                if simple_query_time > 0.1:
                    health_report["recommendations"].append("⚠️ Simple query > 100ms - investigate database performance")
            
            # Test 4: Critical Table Access
            logger.info("🗂️ Testing critical table access...")
            critical_tables = ['tenant_settings', 'business_offerings', 'customer_profiles', 'messages']
            
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for table in critical_tables:
                    try:
                        start_time = time.time()
                        cur.execute(f"SELECT COUNT(*) as count FROM {table}")
                        result = cur.fetchone()
                        access_time = time.time() - start_time
                        
                        health_report["table_access"][table] = {
                            "accessible": True,
                            "row_count": result['count'],
                            "access_time_ms": round(access_time * 1000, 2)
                        }
                    except Exception as e:
                        health_report["table_access"][table] = {
                            "accessible": False,
                            "error": str(e)
                        }
                        health_report["error_log"].append(f"Table {table}: {e}")
            
            conn.close()
            logger.info("✅ CNS Supabase verification completed successfully")
            
        except Exception as e:
            logger.error(f"❌ CNS verification failed: {e}")
            health_report["error_log"].append(str(e))
            health_report["recommendations"].append("🚨 Critical: Check DATABASE_URL and network connectivity")
        
        return health_report
    
    def generate_recommendations(self, health_report: Dict[str, Any]) -> list:
        """Generate CNS-compliant recommendations"""
        recommendations = []
        
        if not health_report["database_url_configured"]:
            recommendations.append("🚨 URGENT: Configure DATABASE_URL in .env file")
        
        if not health_report["basic_connectivity"]:
            recommendations.append("🚨 URGENT: Cannot establish database connection")
            recommendations.append("🔧 Check: Supabase project status, network connectivity, credentials")
        
        if health_report.get("query_performance", {}).get("connection_time_ms", 0) > 2000:
            recommendations.append("⚠️ Performance: Connection time exceeds 2 seconds")
        
        if health_report.get("query_performance", {}).get("simple_query_ms", 0) > 100:
            recommendations.append("⚠️ Performance: Simple query exceeds 100ms")
        
        # Check for missing critical tables
        missing_tables = []
        for table, info in health_report.get("table_access", {}).items():
            if isinstance(info, dict) and not info.get("accessible", False):
                missing_tables.append(table)
        
        if missing_tables:
            recommendations.append(f"🔧 Schema: Missing or inaccessible tables: {', '.join(missing_tables)}")
        
        return recommendations

def main():
    """Execute CNS Task W-04: Verify Supabase Connection Log"""
    logger.info("🪖 CNS Task W-04: Verify Supabase Connection Log")
    logger.info("=" * 60)
    
    verifier = SupabaseConnectionVerifier()
    health_report = verifier.verify_connection_health()
    
    # Generate recommendations
    recommendations = verifier.generate_recommendations(health_report)
    health_report["recommendations"] = recommendations
    
    # Log results
    logger.info("📊 CNS Connection Health Report:")
    logger.info(f"   Database URL Configured: {health_report['database_url_configured']}")
    logger.info(f"   Basic Connectivity: {health_report['basic_connectivity']}")
    logger.info(f"   Connection Time: {health_report.get('query_performance', {}).get('connection_time_ms', 'N/A')}ms")
    logger.info(f"   Public Tables: {health_report.get('table_access', {}).get('public_tables_count', 'N/A')}")
    
    if recommendations:
        logger.warning("⚠️ CNS Recommendations:")
        for rec in recommendations:
            logger.warning(f"   {rec}")
    else:
        logger.info("✅ No issues detected - Supabase connection is optimal")
    
    # Save detailed report
    report_file = ".antigravity/supabase_health_report.json"
    import json
    with open(report_file, 'w') as f:
        json.dump(health_report, f, indent=2)
    
    logger.info(f"📄 Detailed report saved to: {report_file}")
    logger.info("=" * 60)
    logger.info("🎯 CNS Task W-04: COMPLETE")

if __name__ == "__main__":
    main()
