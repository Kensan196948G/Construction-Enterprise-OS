"""Auth service event publishing integration"""

from ceo_os_event_core.models import create_user_event
from ceo_os_event_core.types import EventTypes


# Singleton publisher instance for the auth service
_publisher = None


async def get_event_publisher(bootstrap_servers: str = "localhost:9092"):
    from ceo_os_event_core.publisher import EventPublisher

    global _publisher
    if _publisher is None:
        _publisher = EventPublisher(bootstrap_servers=bootstrap_servers)
        await _publisher.start()
    return _publisher


async def publish_user_created(user_id: str, org_id: str, data: dict):
    publisher = await get_event_publisher()
    event = create_user_event(EventTypes.USER_CREATED, user_id, org_id, data)
    await publisher.publish("ceo-os.users", event.__dict__)


async def publish_user_login(user_id: str, org_id: str, data: dict):
    publisher = await get_event_publisher()
    event = create_user_event(EventTypes.USER_LOGIN, user_id, org_id, data)
    await publisher.publish("ceo-os.users", event.__dict__)


async def publish_user_role_changed(user_id: str, org_id: str, data: dict):
    publisher = await get_event_publisher()
    event = create_user_event(
        EventTypes.USER_ROLE_CHANGED, user_id, org_id, data
    )
    await publisher.publish("ceo-os.users", event.__dict__)


async def publish_user_deactivated(user_id: str, org_id: str, data: dict):
    publisher = await get_event_publisher()
    event = create_user_event(
        EventTypes.USER_DEACTIVATED, user_id, org_id, data
    )
    await publisher.publish("ceo-os.users", event.__dict__)
