import sqlite3
import threading

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def changere_session(user, session_key, user_agent, ip):
    db_path = 'E:/website-seller-fashion-pthon/db.sqlite3'
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_sessions_session
                SET user_agent = ?, ip = ?
                WHERE user_id = ? OR session_key = ?
            """, (user_agent, ip, user, session_key))
            conn.commit()
            print(f"[✓] Updated {cursor.rowcount} session(s)")
    except sqlite3.Error as e:
        print(f"[✗] SQLite error: {e}")

class UpdateSessionInfoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            session_key = request.session.session_key
            timer = threading.Timer(1.0, changere_session, args=(request.user.id, session_key, user_agent, ip))
            timer.start()

        response = self.get_response(request)
        return response
          
