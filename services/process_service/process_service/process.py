import asyncio
import io
import logging
import os
import shutil
from urllib.parse import urlparse

import aioboto3
import aiofiles
import ffmpeg
import redis.asyncio as redis
from zipstream import AioZipStream

from .models import FileProcessedEvent, ProcessFileEventModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcessFileEvent:
    def __init__(
        self,
        redis_client: redis.Redis,
        aws_session: aioboto3.Session,
        event_data: ProcessFileEventModel,
    ):
        self.redis_client = redis_client
        self.aws_session = aws_session
        self.event_data = event_data
        self._output_pattern = "frame_%04d.png"
        self._fps = 0.1

    async def download_file(self) -> str:
        """
        Download a file from S3.
        """
        s3_path = self.event_data.s3_path
        event_id = self.event_data.event_id

        parsed_url = urlparse(s3_path)

        logger.info(f">> Downloading file from S3: {s3_path}")
        logger.info(f">> Bucket name: {parsed_url.netloc}")
        logger.info(f">> parsed_url: {parsed_url}")
        bucket = parsed_url.netloc
        key = parsed_url.path.lstrip("/")  # Remove leading '/' if present.
        file_name = key.split("/")[-1]

        try:
            # Create the directory if it doesn't exist
            os.makedirs(f"./temp/{event_id}", exist_ok=True)
            async with self.aws_session.client("s3") as s3_client:
                async with aiofiles.open(f"./temp/{event_id}/{file_name}", mode="wb") as f:
                    await s3_client.download_fileobj(bucket, key, f)
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return False

        return f"./temp/{event_id}/{file_name}"

    async def process_file(self, file_path: str) -> bool:
        """
        Process the downloaded file.
        """

        # Extract frames from the video
        process = (
            ffmpeg.input(file_path)
            .output(
                f"./temp/{self.event_data.event_id}/{self._output_pattern}", vf=f"fps={self._fps}"
            )
            .run_async()
        )

        stdout, stderr = await asyncio.to_thread(process.communicate)

        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")

        return True

    async def compress_frames(self) -> bool:
        """
        Compress the processed frames into a .zip file.
        """

        # Find matching frame files
        frame_files = [
            {"file": os.path.join(f"./temp/{self.event_data.event_id}", file)}
            for file in sorted(os.listdir(f"./temp/{self.event_data.event_id}"))
            if file.startswith("frame_") and file.endswith(".png")
        ]

        if not frame_files:
            logger.warning("No frames found for compression!")
            return False

        # Create an asynchronous zip stream
        aiozip = AioZipStream(frame_files, chunksize=32768)

        # Write the zip file asynchronously
        async with aiofiles.open(f"./temp/{self.event_data.event_id}/frames.zip", mode="wb") as z:
            async for chunk in aiozip.stream():
                await z.write(chunk)

        logger.info("Frames compressed into frames.zip.")
        return True

    async def upload_zip_to_s3(self):
        """
        Upload the compressed frames to S3.
        """
        s3_path = self.event_data.s3_path

        parsed_url = urlparse(s3_path)
        bucket = parsed_url.netloc
        key = f"{self.event_data.user_id}/{self.event_data.event_id}/frames.zip"

        async with self.aws_session.client("s3") as s3_client:
            async with aiofiles.open(
                f"./temp/{self.event_data.event_id}/frames.zip", mode="rb"
            ) as f:
                file_data = await f.read()
                file_obj = io.BytesIO(file_data)
                await s3_client.upload_fileobj(file_obj, bucket, key)

        return s3_path

    async def clean_up(self):
        """
        Clean up temporary files.
        """
        event_dir = f"./temp/{self.event_data.event_id}"
        try:
            shutil.rmtree(event_dir)
            logger.info(f"Cleaned up temporary directory: {event_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up temporary directory {event_dir}: {e}")

    async def callback(self, s3_path: str):
        file_processed_event = FileProcessedEvent(
            event_id=self.event_data.event_id, s3_path=s3_path, user_id=self.event_data.user_id
        )
        await self.redis_client.publish("saga_events", file_processed_event.model_dump_json())

    async def process(self):
        file_path = await self.download_file()
        logger.info(f"Downloaded file: {file_path}")
        has_processed = await self.process_file(file_path)
        logger.info(f"Processed file: {has_processed}")
        has_compressed = await self.compress_frames()
        logger.info(f"Compressed frames: {has_compressed}")
        s3_path = await self.upload_zip_to_s3()
        logger.info(f"Uploaded frames to S3: {s3_path}")
        await self.clean_up()
        await self.callback(s3_path)
        return True
