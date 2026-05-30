from typing import Any


class PushService:
    async def send_to_user(
        self,
        user_id: str,
        title: str,
        body: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        # Replace this mock with APNs/FCM/UniPush/vendor push integration.
        print({"user_id": user_id, "title": title, "body": body, "payload": payload or {}})

