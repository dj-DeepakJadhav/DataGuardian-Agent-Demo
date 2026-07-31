"""
DuckDB / SQLite Sandbox Runner for DataGuardian Agent.
Executes dry-runs of broken and patched SQL queries for multiple failure scenarios:
1. Upstream Column Schema Drift (renamed user_id -> customer_guid)
2. Null Spike Assertion Breach (unexpected nulls in customer_id)
3. Type Mismatch Drift (amount_usd converted to String formatted with currency symbols '$150.50')
"""

import sqlite3
import logging
from typing import Dict, Any, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SandboxRunner")

class SandboxRunner:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._init_mock_warehouse()

    def _init_mock_warehouse(self):
        cursor = self.conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS source_orders")
        cursor.execute("DROP TABLE IF EXISTS orders_v1")
        
        cursor.execute("""
            CREATE TABLE source_orders (
                id TEXT,
                user_id TEXT,
                total_amount REAL,
                created_at TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO source_orders VALUES 
            ('ord_101', 'usr_88', 150.50, '2026-07-30 10:00:00'),
            ('ord_102', 'usr_99', 200.00, '2026-07-30 11:30:00')
        """)
        
        cursor.execute("""
            CREATE TABLE orders_v1 (
                order_id TEXT,
                customer_id TEXT,
                amount_usd REAL,
                created_at TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO orders_v1 VALUES 
            ('ord_101', 'usr_88', 150.50, '2026-07-30 10:00:00')
        """)
        self.conn.commit()

    def trigger_schema_drift(self):
        """Scenario 1: Column Schema Drift (renaming total_amount -> amount_usd, user_id -> customer_guid)"""
        cursor = self.conn.cursor()
        cursor.execute("DROP TABLE source_orders")
        cursor.execute("""
            CREATE TABLE source_orders (
                id TEXT,
                customer_guid TEXT,
                amount_usd REAL,
                created_at TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO source_orders VALUES 
            ('ord_103', 'usr_100', 350.00, '2026-07-31 02:00:00')
        """)
        self.conn.commit()
        logger.warning("Simulated Scenario 1: Upstream Column Schema Drift!")

    def trigger_null_spike(self):
        """Scenario 2: Null Spike Assertion Breach"""
        cursor = self.conn.cursor()
        cursor.execute("DROP TABLE source_orders")
        cursor.execute("""
            CREATE TABLE source_orders (
                id TEXT,
                user_id TEXT,
                total_amount REAL,
                created_at TEXT
            )
        """)
        # Insert rows with 80% NULL user_id values
        cursor.execute("""
            INSERT INTO source_orders VALUES 
            ('ord_201', NULL, 120.00, '2026-07-31 03:00:00'),
            ('ord_202', NULL, 450.00, '2026-07-31 03:05:00'),
            ('ord_203', 'usr_88', 90.00, '2026-07-31 03:10:00')
        """)
        self.conn.commit()
        logger.warning("Simulated Scenario 2: Upstream Null Spike Anomaly!")

    def trigger_type_mismatch(self):
        """Scenario 3: Type Mismatch Drift ($ string formatted numeric)"""
        cursor = self.conn.cursor()
        cursor.execute("DROP TABLE source_orders")
        cursor.execute("""
            CREATE TABLE source_orders (
                id TEXT,
                user_id TEXT,
                total_amount TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO source_orders VALUES 
            ('ord_301', 'usr_88', '$150.50', '2026-07-31 04:00:00'),
            ('ord_302', 'usr_99', '$200.00', '2026-07-31 04:05:00')
        """)
        self.conn.commit()
        logger.warning("Simulated Scenario 3: Upstream Data Type Mismatch ($ string currency)!")

    def execute_query(self, sql_query: str) -> Tuple[bool, Any]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            return True, rows
        except Exception as e:
            return False, str(e)
