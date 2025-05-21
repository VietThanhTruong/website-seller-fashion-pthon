from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import pre_save, post_save, post_delete
from django.contrib.auth.models import User
from .models import UserProfile
from .models import Product
from django.forms.models import model_to_dict
from django.db.models.fields.files import FieldFile
from django.dispatch import receiver
from user_sessions.models import Session as UserSessionModel
import sqlite3
import threading
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# SAVE IP AND USER AGENT TO DB
def changere_session(user, session_key, user_agent, ip):
    BASE_DIR = Path(__file__).resolve().parent.parent
    db_path = BASE_DIR / 'db.sqlite3'
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_sessions_session
                SET user_agent = ?, ip = ?
                WHERE user_id = ? OR session_key = ?
            """, (user_agent, ip, user, session_key))
            conn.commit()
            # print(f"[✓] Updated {cursor.rowcount} session(s)")
    except sqlite3.Error as e:
        print(f"[✗] SQLite error: {e}")
          
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    current_session_key = request.session.session_key

    user_sessions = UserSessionModel.objects.filter(user=user).exclude(session_key=current_session_key)
    for session in user_sessions:
        session.delete()

    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
    try:
        session = UserSessionModel.objects.get(session_key=current_session_key)
        timer = threading.Timer(1.0, changere_session, args=(user.id, session.session_key, user_agent, ip))
        timer.start()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        pass
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        pass

def get_changed_fields(old_instance, new_instance):
    old_data = model_to_dict(old_instance)
    new_data = model_to_dict(new_instance)
    
    changes = {}
    for field in new_data.keys():
        old_val = old_data.get(field)
        new_val = new_data.get(field)

        if isinstance(old_val, FieldFile):
            old_val = old_val.name
        if isinstance(new_val, FieldFile):
            new_val = new_val.name

        if old_val != new_val:
            changes[field] = {'old': old_val, 'new': new_val}
    return changes

@receiver(pre_save, sender=Product)
def cache_old_instance(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None

@receiver(post_save, sender=Product)
def log_product_save(sender, instance, created, **kwargs):
    user = getattr(instance, '_modified_by', None)
    action = 'Created' if created else 'Updated'

    if created:
        logger.info(f"Product Created: {instance.id} - {instance.name} by user {user}")
    else:
        old_instance = getattr(instance, '_old_instance', None)
        if old_instance:
            # old_instance = sender.objects.get(pk=instance.pk)
            changes = get_changed_fields(old_instance, instance)
            changes_str = "; ".join([
                f"{field}: '{str(v['old'])}' -> '{str(v['new'])}'"
                for field, v in changes.items()
            ])
            logger.info(f"Product Updated: {instance.id} - {instance.name} by user {user}. Changes: {str(changes_str)}")
        else:
            logger.info(f"Product Updated: {instance.id} - {instance.name} by user {user}. No fields changed.")

@receiver(post_delete, sender=Product)
def log_product_delete(sender, instance, **kwargs):
    user = getattr(instance, '_modified_by', None)
    logger.info(f"Product Deleted: {instance.id} - {instance.name} by user {user}")

class UpdateSessionInfoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if '/checkout' not in request.path:
                for key in ['selected_items', 'total_price', 'oderKey', 'selected_contact_id', 'voucher_code', 'items']:
                    if key in request.session:
                        del request.session[key]

            ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            session_key = request.session.session_key
            timer = threading.Timer(1.0, changere_session, args=(request.user.id, session_key, user_agent, ip))
            timer.start()

        response = self.get_response(request)
        return response

# USERS PROFILE
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        profile = instance.userprofile
        profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()