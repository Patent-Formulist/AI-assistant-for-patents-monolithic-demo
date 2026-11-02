-- Пользователь admin создаётся автоматически через POSTGRES_USER
-- База formulist создаётся автоматически через POSTGRES_DB
-- Этот файл для дополнительной инициализации схемы

\c formulist

GRANT ALL ON SCHEMA public TO admin;
