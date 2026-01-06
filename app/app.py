from flask import Flask, jsonify, request
import redis
import psycopg2
import os

app = Flask(__name__)

# Redis (shared connection)
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    decode_responses=True
)

# Postgres (one connection at startup)
db_conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
db_cur = db_conn.cursor()

@app.route("/health")
def health():
    try:
        # Redis: اتصال جديد + timeout
        test_redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=6379,
            socket_connect_timeout=1,
            socket_timeout=1
        )
        test_redis.ping()

        # DB: اتصال جديد
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            connect_timeout=1
        )

        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "reason": str(e)
        }), 500



@app.route("/")
def home():
    redis_client.incr("visits")
    visits = redis_client.get("visits")

    db_cur.execute("SELECT 1;")

    return jsonify({
        "message": "natooooooooo  🚀",
        "visits": visits,
        "from_nginx": request.headers.get("X-From-Nginx")
    })


