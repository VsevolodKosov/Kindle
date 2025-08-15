## Баг 1
**Упал тест:** `test_create_user_without_some_fields[payload8-201]`

**Лог:** `AttributeError: 'NoneType' object has no attribute 'id'`

**Возможные причины:**
1. В DAO поле `bio` имеет тип `str`, а в схеме `Optional[str]`. Когда `bio=None`, DAO не может обработать.
2. В модели `User` поле `bio` определено как `Mapped[str]` без `nullable=True`, но в схеме `Optional[str]`. SQLAlchemy не может сохранить `None` в поле, которое не помечено как nullable.

**Варианты исправления:**
1. Изменить в DAO `bio: str` на `bio: Optional[str]` в `create_user`
2. Изменить в модели `bio: Mapped[str] = mapped_column(Text)` на `bio: Mapped[str] = mapped_column(Text, nullable=True)`
3. Сделать новую миграцию

---

## Текущее покрытие тестами

### Общая статистика покрытия:
- **Общее покрытие: 90%** (816 строк кода, 78 непокрытых строк)
- **Основной код: 87%** (498 строк кода, 64 непокрытых строк)
