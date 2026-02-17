

import os
import logging
import requests
from typing import Annotated, Any, Dict
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.modules.channels.meta.dtos.inbound import Audio, Image, Message, Payload, RoleType, User
from src.core.di.container import Container

IS_DEV_ENVIRONMENT = True

app = FastAPI(
    title="WhatsApp Bot",
    version="0.1.0",
    openapi_url=f"/openapi.json" if IS_DEV_ENVIRONMENT else None,
    docs_url=f"/docs" if IS_DEV_ENVIRONMENT else None,
    redoc_url=f"/redoc" if IS_DEV_ENVIRONMENT else None,
    swagger_ui_oauth2_redirect_url=f"/docs/oauth2-redirect" if IS_DEV_ENVIRONMENT else None,
)

log = logging.getLogger(__name__)

container = Container()
setattr(app, "container", container)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

meta_service = container.meta.meta_service()


def parse_message(payload: Payload) -> Message | None:
    if not payload.entry[0].changes[0].value.messages:
        return None
    return payload.entry[0].changes[0].value.messages[0]


def get_current_user(message: Annotated[Message, Depends(parse_message)]) -> User | None:
    if not message:
        return None
    
    # TODO: Authenticate user by phone number 
    # -> meta_service.authenticate_user_by_phone_number(message.from_)
    return User(id=1, phone="5511991490733", first_name="lennon", last_name="bahia", role=RoleType.BASIC)


def parse_audio_file(message: Annotated[Message, Depends(parse_message)]) -> Audio | None:
    if message and message.type == "audio":
        return message.audio
    return None


def parse_image_file(message: Annotated[Message, Depends(parse_message)]) -> Image | None:
    if message and message.type == "image":
        return message.image
    return None


def message_extractor(
        message: Annotated[Message, Depends(parse_message)],
        audio: Annotated[Audio, Depends(parse_audio_file)],
):
    if audio:
        return "" # message_service.transcribe_audio(audio)
    if message and message.text:
        return message.text.body
    return None


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/readiness")
def readiness():
    return {"status": "ready"}

@app.get("/keep-alive-webhook")
def keep_alive_webhook():
    public_url = os.environ.get("PUBLIC_URL") or os.environ.get("NGROK_PUBLIC_URL")
    checks = {"webhook_get": None, "ngrok_local": None}
    if public_url:
        try:
            token = os.environ.get("VERIFICATION_TOKEN", "my_voice_is_my_password_verify_me")
            challenge = 123456
            r_get = requests.get(
                public_url.rstrip("/") + "/webhook",
                params={"hub.mode": "subscribe", "hub.challenge": challenge, "hub.verify_token": token},
                timeout=3,
            )
            checks["webhook_get"] = r_get.status_code == 200 and str(r_get.text).strip() == str(challenge)
        except Exception:
            checks["webhook_get"] = False

    ngrok_api = os.environ.get("NGROK_API_URL", "http://127.0.0.1:4040")
    ngrok_tunnels = None
    try:
        r_tunnels = requests.get(ngrok_api.rstrip("/") + "/api/tunnels", timeout=2)
        if r_tunnels.status_code == 200:
            data = r_tunnels.json()
            tunnels = data.get("tunnels", [])
            ngrok_tunnels = [
                {
                    "name": t.get("name"),
                    "public_url": t.get("public_url"),
                    "proto": t.get("proto"),
                    "addr": t.get("config", {}).get("addr"),
                }
                for t in tunnels
            ]
            checks["ngrok_local"] = True
        else:
            checks["ngrok_local"] = False
    except Exception:
        checks["ngrok_local"] = False

    reachable = None if not public_url else (checks["webhook_get"] is True)

    return {
        "status": "ok",
        "public_url": public_url,
        "checks": checks,
        "reachable": reachable,
        "ngrok_tunnels": ngrok_tunnels,
        "ngrok_api": ngrok_api,
    }


@app.get("/webhook")
def verify_whatsapp(
        hub_mode: str = Query("subscribe", description="The mode of the webhook", alias="hub.mode"),
        hub_challenge: int = Query(..., description="The challenge to verify the webhook", alias="hub.challenge"),
        hub_verify_token: str = Query(..., description="The verification token", alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == os.environ.get("VERIFICATION_TOKEN", "my_voice_is_my_password_verify_me"):
        return hub_challenge

    raise HTTPException(status_code=403, detail="Invalid verification token")


@app.post("/webhook", status_code=200)
async def receive_whatsapp(
        data: Dict[Any, Any],
        user: Annotated[User, Depends(get_current_user)],
        user_message: Annotated[str, Depends(message_extractor)],
        image: Annotated[Image, Depends(parse_image_file)],
        message: Annotated[Message, Depends(parse_message)],
):
    payload = Payload(**data)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if image:
        print("Image received")
        return {"status": "ok"}

    if user_message:
        print(f"Received message from user {user.first_name} {user.last_name} ({user.phone})")
        await meta_service.send_message("1", message.from_, user.phone, user_message)

    return {"status": "ok"}
