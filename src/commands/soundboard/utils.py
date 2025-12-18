import json
import os
from pathlib import Path
import time
from typing import Any, Dict, List
import boto3
from cloudflare import Cloudflare
from discord import app_commands
import discord
from dotenv import load_dotenv


class Sounds:
    name: str
    file_name: str


# Setting up to load ENV values
load_dotenv()


class Config:
    # Cache configuration
    CACHE_DIR = Path("cache")
    CACHE_FILE = CACHE_DIR / "sounds_cache.json"
    CACHE_TIMESTAMP_FILE = CACHE_DIR / "sounds_cache_timestamp.txt"
    CACHE_EXPIRY_SECONDS = 300  # 5 minutes

    # Cloudflare Database
    CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
    CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    CLOUDFLARE_DATABASE_ID = os.getenv("CLOUDFLARE_DATABASE_ID")
    CLOUDFLARE_TABLE_NAME = os.getenv("CLOUDFLARE_TABLE_NAME")

    # Cloudflare S3
    CLOUDFLARE_ENDPOINT_URL = os.getenv("CLOUDFLARE_ENDPOINT_URL")
    CLOUDFLARE_ACCESS_KEY_ID = os.getenv("CLOUDFLARE_ACCESS_KEY_ID")
    CLOUDFLARE_SECRET_ACCESS_KEY = os.getenv("CLOUDFLARE_SECRET_ACCESS_KEY")
    CLOUDFLARE_BUCKET_NAME = os.getenv("CLOUDFLARE_BUCKET_NAME")
    CLOUDFLARE_REGION_NAME = os.getenv("CLOUDFLARE_REGION_NAME")

    # Soundboard directory
    SOUNDBOARD_DIR = "soundboard"


class ErrorMessages:
    DATABASE_CLIENT = "❌ Could not connect to Cloudflare database client."
    S3_CLIENT = "❌ Could not connect to Cloudflare S3 client."
    DATABASE = "Could not connect to database."
    DOWNLOAD_SOUND = "❌ Could not download sound"
    NO_SOUNDS = "❌ No sounds available."
    UPLOAD_S3 = "Could not upload sound file to S3."
    UPLOAD_DATABASE = "Could not upload sound file to database."
    DELETE_S3 = "Could not delete sound file from S3 storage."
    DELETE_DATABASE = "Could not delete sound from database."


class Sound:
    def __init__(self, name: str, file_name: str):
        self.name = name
        self.file_name = file_name


class SoundCache:
    @staticmethod
    def ensure_cache_dir():
        """Ensure cache directory exists"""
        Config.CACHE_DIR.mkdir(exist_ok=True)
        (Config.CACHE_DIR / "sounds").mkdir(exist_ok=True)

    @staticmethod
    def is_valid() -> bool:
        """Check if cache is still valid"""
        if not Config.CACHE_TIMESTAMP_FILE.exists():
            return False

        try:
            with open(Config.CACHE_TIMESTAMP_FILE, "r") as f:
                timestamp = float(f.read().strip())
            return (time.time() - timestamp) < Config.CACHE_EXPIRY_SECONDS
        except (ValueError, IOError):
            return False

    @staticmethod
    def save(sounds_data: List[Dict[str, Any]]):
        """Save sounds data to cache"""
        SoundCache.ensure_cache_dir()

        with open(Config.CACHE_FILE, "w") as f:
            json.dump(sounds_data, f)

        with open(Config.CACHE_TIMESTAMP_FILE, "w") as f:
            f.write(str(time.time()))

    @staticmethod
    def load() -> List[Dict[str, Any]]:
        """Load sounds data from cache"""
        if not Config.CACHE_FILE.exists():
            return []

        try:
            with open(Config.CACHE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    @staticmethod
    def invalidate():
        """Invalidate the sounds cache"""
        Config.CACHE_FILE.unlink(missing_ok=True)
        Config.CACHE_TIMESTAMP_FILE.unlink(missing_ok=True)


class ClientFactory:
    @staticmethod
    def get_database_client() -> Cloudflare:
        """Get Cloudflare database client"""
        try:
            return Cloudflare(api_token=Config.CLOUDFLARE_API_TOKEN)
        except Exception:
            raise ValueError(ErrorMessages.DATABASE_CLIENT)

    @staticmethod
    def get_s3_client():
        """Get Cloudflare S3 client"""
        try:
            return boto3.client(
                service_name="s3",
                endpoint_url=Config.CLOUDFLARE_ENDPOINT_URL,
                aws_access_key_id=Config.CLOUDFLARE_ACCESS_KEY_ID,
                aws_secret_access_key=Config.CLOUDFLARE_SECRET_ACCESS_KEY,
                region_name=Config.CLOUDFLARE_REGION_NAME,
            )
        except Exception:
            raise ValueError(ErrorMessages.S3_CLIENT)


class DatabaseOperations:
    @staticmethod
    def get_all_sounds() -> List[Dict[str, Any]]:
        """Get all sounds from database"""
        if SoundCache.is_valid():
            cached_data = SoundCache.load()
            if cached_data:
                return cached_data

        client = ClientFactory.get_database_client()
        try:
            query = f"SELECT * FROM {Config.CLOUDFLARE_TABLE_NAME};"
            response = client.d1.database.query(
                database_id=Config.CLOUDFLARE_DATABASE_ID,
                account_id=Config.CLOUDFLARE_ACCOUNT_ID,
                sql=query,
            )
        except Exception:
            raise ValueError(ErrorMessages.DATABASE)

        sound_items = response.result[0].results

        if not sound_items:
            SoundCache.save([])
            raise ValueError(ErrorMessages.NO_SOUNDS)

        SoundCache.save(sound_items)
        return sound_items

    @staticmethod
    def add_sound(name: str, file_name: str) -> None:
        """Add sound to database"""
        client = ClientFactory.get_database_client()
        try:
            query = f"""
                INSERT INTO "{Config.CLOUDFLARE_TABLE_NAME}" (name, file_name) 
                VALUES (:name, :file_name);
            """

            client.d1.database.query(
                database_id=Config.CLOUDFLARE_DATABASE_ID,
                account_id=Config.CLOUDFLARE_ACCOUNT_ID,
                sql=query,
                params=[name, file_name],
            )
        except Exception as e:
            raise ValueError(f"{ErrorMessages.UPLOAD_DATABASE}: {str(e)}")

    @staticmethod
    def delete_sound(name: str) -> None:
        """Delete sound from database"""
        client = ClientFactory.get_database_client()
        try:
            query = f"""
                DELETE FROM "{Config.CLOUDFLARE_TABLE_NAME}" 
                WHERE name = :name;
            """

            client.d1.database.query(
                database_id=Config.CLOUDFLARE_DATABASE_ID,
                account_id=Config.CLOUDFLARE_ACCOUNT_ID,
                sql=query,
                params=[name],
            )
        except Exception as e:
            raise ValueError(f"{ErrorMessages.DELETE_DATABASE}: {str(e)}")


class S3Operations:
    @staticmethod
    async def upload_file(file: discord.Attachment) -> None:
        """Upload file to S3"""
        s3 = ClientFactory.get_s3_client()
        try:
            file_data = await file.read()
            s3.put_object(
                Bucket=Config.CLOUDFLARE_BUCKET_NAME,
                Key=f"{Config.SOUNDBOARD_DIR}/{file.filename}",
                Body=file_data,
                ContentType=file.content_type,
            )
        except Exception:
            raise ValueError(ErrorMessages.UPLOAD_S3)

    @staticmethod
    def delete_file(file_name: str) -> None:
        """Delete file from S3"""
        s3 = ClientFactory.get_s3_client()
        try:
            s3.delete_object(
                Bucket=Config.CLOUDFLARE_BUCKET_NAME,
                Key=f"{Config.SOUNDBOARD_DIR}/{file_name}",
            )
        except Exception:
            raise ValueError(ErrorMessages.DELETE_S3)

    @staticmethod
    def download_file(file_name: str) -> None:
        """Download file from S3"""
        s3 = ClientFactory.get_s3_client()
        try:
            local_path = Config.CACHE_DIR / "sounds" / file_name
            s3.download_file(
                Config.CLOUDFLARE_BUCKET_NAME,
                f"{Config.SOUNDBOARD_DIR}/{file_name}",
                str(local_path),
            )
        except Exception:
            raise ValueError(ErrorMessages.DOWNLOAD_SOUND)


class FileOperations:
    @staticmethod
    def delete_local_file(file_name: str) -> None:
        """Delete local cached file"""
        file_path = Config.CACHE_DIR / "sounds" / file_name
        if file_path.exists():
            file_path.unlink()


def get_sounds() -> List[Dict[str, Any]]:
    """Get all sounds (cached or from database)"""
    return DatabaseOperations.get_all_sounds()


async def upload_sound_file(name: str, file: discord.Attachment) -> None:
    """Upload sound file to S3 and database"""
    try:
        await S3Operations.upload_file(file)
        DatabaseOperations.add_sound(name, file.filename)
        SoundCache.invalidate()
    except Exception as e:
        raise ValueError(f"Could not upload sound file: {e}")


async def delete_sound(name: str, file_name: str) -> None:
    """Delete sound from S3, database, and local cache"""
    try:
        S3Operations.delete_file(file_name)
        DatabaseOperations.delete_sound(name)
        FileOperations.delete_local_file(file_name)
        SoundCache.invalidate()
    except Exception as e:
        raise ValueError(f"Could not delete sound file: {e}")


def download_sound_file(file_name: str) -> None:
    """Download sound file from S3 to local cache"""
    S3Operations.download_file(file_name)


async def autocomplete_sound_name(current: str) -> List[app_commands.Choice[str]]:
    """Generate autocomplete choices for sound names"""
    try:
        sounds = get_sounds()
        filtered_sounds = [
            sound for sound in sounds if current.lower() in sound["name"].lower()
        ]
        return [
            app_commands.Choice(name=sound["name"], value=sound["name"])
            for sound in filtered_sounds[:25]  # Discord limit
        ]
    except Exception:
        return []
