import sys
import os

sys.path.insert(0, '/home/dvwuutxc/project')

# Thiết lập biến môi trường
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')  # sửa nếu tên khác

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
