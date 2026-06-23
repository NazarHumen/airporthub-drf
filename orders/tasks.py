from celery import shared_task

from orders.services import release_expired_orders


@shared_task
def cancel_unpaid_orders():
    """Backup to lazy expiry: cancel pending orders past their deadline."""
    return release_expired_orders()
