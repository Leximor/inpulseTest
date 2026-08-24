from django.db import transaction

from .models import Profile, Transaction, User


@transaction.atomic
def process_user_transactions(user: User) -> None:
    """Пометить все транзакции пользователя как processed и выставить флаг в профиле.

    Всё выполняется в одной транзакции БД:
    - select_for_update() блокирует строки профиля и транзакций до COMMIT;
    - каждая транзакция сохраняется через save() (без bulk_update);
    - любое исключение откатывает и статусы, и флаг профиля.
    """
    profile = Profile.objects.select_for_update().get(user_id=user.pk)

    user_transactions = Transaction.objects.select_for_update().filter(user_id=user.pk)

    for tx in user_transactions:
        tx.status = "processed"
        tx.save(update_fields=["status", "updated_at"])

    profile.has_processed_transactions = True
    profile.save(update_fields=["has_processed_transactions"])
