import os
import sys
import json
from pathlib import Path
from typing import Optional, List

import psycopg2
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.config.settings import settings


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL não está definido no ambiente")
    return database_url


def upsert_meta_account(
    conn,
    name: str,
    meta_business_account_id: str,
    phone_number_id: str,
    meta_phone_number: str,
    system_user_access_token: Optional[str],
    webhook_verification_token: Optional[str],
    phone_numbers: Optional[List[str]] = None,
) -> None:
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id FROM meta_accounts
        WHERE meta_business_account_id = %s
        FOR UPDATE
        """,
        (meta_business_account_id,),
    )
    row = cursor.fetchone()

    if row:
        account_id = row[0]
        cursor.execute(
            """
            UPDATE meta_accounts
            SET
                phone_number_id = %s,
                meta_phone_number = %s,
                system_user_access_token = %s,
                webhook_verification_token = %s,
                phone_numbers = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                phone_number_id,
                meta_phone_number,
                system_user_access_token,
                webhook_verification_token,
                json.dumps(phone_numbers or []),
                account_id,
            ),
        )
    else:
        cursor.execute(
            """
            INSERT INTO meta_accounts (
                name,
                meta_business_account_id,
                phone_number_id,
                meta_phone_number,
                system_user_access_token,
                webhook_verification_token,
                phone_numbers
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                name,
                meta_business_account_id,
                phone_number_id,
                meta_phone_number,
                system_user_access_token,
                webhook_verification_token,
                json.dumps(phone_numbers or []),
            ),
        )

    cursor.close()


def main() -> None:
    load_dotenv()

    # Carrega valores de settings.meta
    meta_settings = settings.meta

    bearer_token = meta_settings.bearer_token_access
    verification_token = meta_settings.verification_token
    phone_number_id = meta_settings.phone_number_id
    phone_number = meta_settings.phone_number
    business_account_id = meta_settings.business_account_id

    if not all([bearer_token, verification_token, phone_number_id, phone_number, business_account_id]):
        print(
            "Erro: META_BEARER_TOKEN_ACCESS, META_VERIFICATION_TOKEN, META_PHONE_NUMBER_ID, "
            "META_PHONE_NUMBER e META_BUSINESS_ACCOUNT_ID "
            "precisam estar definidos no .env"
        )
        sys.exit(1)

    # Campos auxiliares
    name = "Default Meta Account"
    meta_business_account_id = business_account_id
    meta_phone_number = phone_number

    # Define lista de phone_numbers incluindo o número principal e o adicional solicitado
    phone_numbers: List[str] = []
    if phone_number:
        phone_numbers.append(phone_number)
    extra_number = "5511991490733"
    if extra_number not in phone_numbers:
        phone_numbers.append(extra_number)

    database_url = get_database_url()

    try:
        conn = psycopg2.connect(database_url)
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")
        sys.exit(1)

    try:
        upsert_meta_account(
            conn=conn,
            name=name,
            meta_business_account_id=meta_business_account_id,
            phone_number_id=phone_number_id,
            meta_phone_number=meta_phone_number,
            system_user_access_token=bearer_token,
            webhook_verification_token=verification_token,
            phone_numbers=phone_numbers,
        )
        conn.commit()
        print("Seed de meta_accounts aplicado com sucesso.")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao executar seed de meta_accounts: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
