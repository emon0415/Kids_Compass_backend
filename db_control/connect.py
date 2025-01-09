import platform
from sqlalchemy import create_engine
import os
import tempfile
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

# 環境変数から設定値を取得
CONNECT = os.getenv("CONNECT")
DATABASE_URL = os.getenv("DATABASE_URL")
pem_content = os.getenv("SSL_CA_CERT")  # 環境変数から取得

def get_db_connection():
    global pem_content  # グローバル変数として宣言

    if CONNECT == "local":
        print("===> Connect to LocalDB ===")
        # ローカル環境のエンジン接続
        engine = create_engine(os.getenv("DB"), echo=True)
        return engine.connect()
    else:
        print("===> Connect to AzureDB ===")

        # SSL証明書が設定されていない場合はエラー
        if pem_content is None or pem_content.strip() == "":
            print(f"SSL_CA_CERT: {pem_content}")  # デバッグ用
            raise ValueError("SSL_CA_CERT is not set or is empty in environment variables.")

        # 環境変数内の証明書内容を整形
        pem_content = pem_content.replace("\\n", "\n").replace("\r", "")

        # 一時ファイルにSSL証明書を保存
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".pem") as temp_pem:
            temp_pem.write(pem_content)
            temp_pem_path = temp_pem.name

        # 証明書ファイルパスを使用してエンジンを作成
        engine = create_engine(
            DATABASE_URL,
            connect_args={
                "ssl": {
                    "ca": temp_pem_path
                }
            }
        )
        return engine.connect()
