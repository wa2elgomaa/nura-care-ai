"""
Storage Service Client for Python services
Handles all file operations via HTTP API to nura-storage service
"""
import os
import logging
from typing import Optional, Dict, List
import httpx
from pathlib import Path

logger = logging.getLogger(__name__)


class StorageClient:
    """HTTP client for nura-storage service"""

    def __init__(self, storage_url: Optional[str] = None):
        self.storage_url = storage_url or os.getenv(
            'STORAGE_SERVICE_URL',
            'http://nura-storage:3012'
        )
        self.client = httpx.AsyncClient(timeout=60.0)
        logger.info(f"StorageClient initialized: {self.storage_url}")

    async def save_file(
        self,
        file_data: bytes,
        category: str,
        filename: str
    ) -> Dict:
        """
        Save file to storage

        Args:
            file_data: File content as bytes
            category: Storage category (e.g., 'enrollments', 'exports')
            filename: Filename

        Returns:
            Dict with 'success', 'path', 'size'
        """
        try:
            files = {'file': (filename, file_data)}
            response = await self.client.post(
                f"{self.storage_url}/storage/upload/{category}",
                files=files
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"✓ Saved to storage: {category}/{filename} ({result.get('size')} bytes)")
            return result
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise

    async def save_from_path(
        self,
        file_path: Path,
        category: str,
        filename: Optional[str] = None
    ) -> Dict:
        """
        Save file from local path to storage

        Args:
            file_path: Local file path
            category: Storage category
            filename: Optional filename (defaults to original filename)

        Returns:
            Dict with 'success', 'path', 'size'
        """
        if filename is None:
            filename = file_path.name

        with open(file_path, 'rb') as f:
            file_data = f.read()

        return await self.save_file(file_data, category, filename)

    async def get_file(
        self,
        category: str,
        filename: str
    ) -> bytes:
        """
        Download file from storage

        Args:
            category: Storage category
            filename: Filename

        Returns:
            File content as bytes
        """
        try:
            response = await self.client.get(
                f"{self.storage_url}/storage/download/{category}/{filename}"
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Failed to get file: {e}")
            raise

    async def get_metadata(
        self,
        category: str,
        filename: str
    ) -> Dict:
        """
        Get file metadata

        Args:
            category: Storage category
            filename: Filename

        Returns:
            Dict with 'exists', 'size', 'createdAt', 'path'
        """
        try:
            response = await self.client.get(
                f"{self.storage_url}/storage/metadata/{category}/{filename}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get metadata: {e}")
            raise

    async def delete_file(
        self,
        category: str,
        filename: str
    ) -> Dict:
        """
        Delete file from storage

        Args:
            category: Storage category
            filename: Filename

        Returns:
            Dict with 'success', 'message'
        """
        try:
            response = await self.client.delete(
                f"{self.storage_url}/storage/{category}/{filename}"
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"✓ Deleted from storage: {category}/{filename}")
            return result
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            raise

    async def list_files(
        self,
        category: str
    ) -> List[str]:
        """
        List files in a category

        Args:
            category: Storage category

        Returns:
            List of filenames
        """
        try:
            response = await self.client.get(
                f"{self.storage_url}/storage/list/{category}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

    async def get_stats(self) -> Dict:
        """
        Get storage statistics

        Returns:
            Dict with storage stats
        """
        try:
            response = await self.client.get(
                f"{self.storage_url}/storage/stats"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise

    async def exists(
        self,
        category: str,
        filename: str
    ) -> bool:
        """
        Check if file exists

        Args:
            category: Storage category
            filename: Filename

        Returns:
            True if file exists
        """
        try:
            metadata = await self.get_metadata(category, filename)
            return metadata.get('exists', False)
        except:
            return False

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_storage_client: Optional[StorageClient] = None


def get_storage_client() -> StorageClient:
    """Get singleton storage client instance"""
    global _storage_client
    if _storage_client is None:
        _storage_client = StorageClient()
    return _storage_client
