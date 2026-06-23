-- ==========================================================
-- راه‌اندازی دیتابیس پروژه فروشگاه
-- این اسکریپت را در pgAdmin > Query Tool اجرا کن
-- ==========================================================

-- 1) ساخت دیتابیس (اگر وجود ندارد)
-- این دستور را جداگانه در Query Tool اجرا کن (روی postgres database)
CREATE DATABASE shop_db
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en-US'
    LC_CTYPE = 'en-US'
    TEMPLATE = template0;

-- ==========================================================
-- بعد از ساخت دیتابیس، به shop_db وصل شو و بقیه را اجرا کن
-- ==========================================================

-- 2) Extension های مورد نیاز
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- برای جستجوی سریع‌تر

-- 3) Schema پیش‌فرض public را تأیید کن
SET search_path TO public;

-- ==========================================================
-- تمام جداول توسط Django migrations ساخته می‌شوند
-- بعد از اجرای این فایل، دستورات زیر را در ترمینال بزن:
--
--   cd my_shop_backend
--   pip install -r requirements.txt
--   python manage.py migrate
--   python manage.py create_admin --email=admin@shop.com --password=Admin@1234
--
-- ==========================================================
