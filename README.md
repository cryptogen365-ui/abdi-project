# STRATIVA

نسخه توسعه‌ای پلتفرم فارسی مدیریت استراتژی و عملکرد، شامل داشبورد React و API مبتنی بر FastAPI/PostgreSQL.

## اجرای کامل با دیتابیس

1. Docker Desktop و Node.js 20+ را نصب کنید.
2. در پوشه پروژه اجرا کنید:

```powershell
docker compose up -d --build
npm install
npm run dev
```

رابط کاربری در `http://localhost:5173`، مستندات API در `http://localhost:8000/docs` و PostgreSQL روی پورت `5432` در دسترس است.

برای توقف سرویس‌ها:

```powershell
docker compose down
```

اطلاعات دیتابیس در volume به نام `strativa_pgdata` حفظ می‌شود. برای محیط واقعی، رمز عبور نمونه را حتماً تغییر دهید.
