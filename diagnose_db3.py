import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# The original URL: postgresql://postgres.wfccfllcbnlepudnokpu:100200300aA@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
# The 5432 pooler URL: postgresql://postgres.wfccfllcbnlepudnokpu:100200300aA@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
# To bypass IPv6 for Supabase direct connection, the Supabase standard for IPv4 is:
# ipv4.db.wfccfllcbnlepudnokpu.supabase.co or using the Pooler Session mode on port 5432.
# Let's try IPv4 direct connection first:

ipv4_url = "postgresql://postgres:100200300aA@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?options=project%3Dwfccfllcbnlepudnokpu"
# According to Supabase docs for connection pooling with PgBouncer:
# Host: aws-0-[region].pooler.supabase.com
# Port: 6543
# Database: postgres
# Username: postgres.[project-ref]
# Password: [password]

print("Trying correctly formatted pooler URL...")
correct_pooler_url = "postgresql://postgres.wfccfllcbnlepudnokpu:100200300aA@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

try:
    conn = psycopg2.connect(correct_pooler_url)
    print(" Connected successfully to Corrected Pooler URL!")
    conn.close()
except Exception as e:
    print(f" Failed on Corrected Pooler URL: {e}")

# What if the region is wrong?
import socket

print("Resolving aws-0-eu-central-1.pooler.supabase.com...")
try:
    print(socket.gethostbyname("aws-0-eu-central-1.pooler.supabase.com"))
except Exception as e:
    print(e)
