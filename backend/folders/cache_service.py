"""
キャッシュサービス: フォルダ構造のキャッシュとバッチ検索を管理
"""
import logging
import time
from datetime import datetime, timedelta
from collections import deque
from typing import List, Dict, Optional
from django.conf import settings
from django.utils import timezone
from googleapiclient.http import BatchHttpRequest
from .models import FolderCache


logger = logging.getLogger(__name__)


class FolderCacheService:
    """フォルダ構造のキャッシュ管理サービス"""

    def __init__(self, service):
        """
        Args:
            service: Google Drive API service instance
        """
        self.service = service
        self.max_age_hours = getattr(settings, 'FOLDER_CACHE_MAX_AGE_HOURS', 24)

    def get_all_folder_ids(self, root_folder_id: str, force_refresh: bool = False) -> List[str]:
        """
        全フォルダIDを取得（キャッシュから、または再構築）

        Args:
            root_folder_id: ルートフォルダID
            force_refresh: True の場合、キャッシュを無視して再構築

        Returns:
            フォルダIDのリスト
        """
        # キャッシュの鮮度をチェック
        cache_is_fresh = self._is_cache_fresh(root_folder_id)

        if not force_refresh and cache_is_fresh:
            logger.info(f"Using cached folder structure for {root_folder_id}")
            folder_ids = self._get_cached_folder_ids(root_folder_id)
            if folder_ids:
                return folder_ids

        # キャッシュが古いか存在しない場合、再構築
        logger.info(f"Rebuilding folder cache for {root_folder_id}")
        return self.build_folder_cache(root_folder_id)

    def _is_cache_fresh(self, root_folder_id: str) -> bool:
        """
        キャッシュが新鮮かチェック

        Args:
            root_folder_id: ルートフォルダID

        Returns:
            True if cache is fresh, False otherwise
        """
        try:
            root_cache = FolderCache.objects.filter(folder_id=root_folder_id).first()
            if not root_cache:
                return False

            age_threshold = timezone.now() - timedelta(hours=self.max_age_hours)
            return root_cache.last_updated > age_threshold
        except Exception as e:
            logger.error(f"Error checking cache freshness: {e}")
            return False

    def _get_cached_folder_ids(self, root_folder_id: str) -> List[str]:
        """
        キャッシュから全フォルダIDを取得

        Args:
            root_folder_id: ルートフォルダID

        Returns:
            フォルダIDのリスト
        """
        try:
            # ルートを含むすべてのフォルダを取得
            folders = FolderCache.objects.filter(is_active=True).values_list('folder_id', flat=True)
            folder_ids = list(folders)

            if root_folder_id not in folder_ids:
                folder_ids.insert(0, root_folder_id)

            logger.info(f"Retrieved {len(folder_ids)} folders from cache")
            return folder_ids
        except Exception as e:
            logger.error(f"Error retrieving cached folder IDs: {e}")
            return []

    def build_folder_cache(self, root_folder_id: str) -> List[str]:
        """
        BFSトラバーサルでフォルダキャッシュを構築

        Args:
            root_folder_id: ルートフォルダID

        Returns:
            フォルダIDのリスト
        """
        start_time = time.time()
        all_folder_ids = []

        try:
            # BFS (Breadth-First Search) でフォルダツリーをトラバース
            queue = deque([(root_folder_id, None, "Root")])
            visited = set()

            while queue:
                folder_id, parent_id, folder_name = queue.popleft()

                if folder_id in visited:
                    continue

                visited.add(folder_id)
                all_folder_ids.append(folder_id)

                # キャッシュに保存
                try:
                    FolderCache.objects.update_or_create(
                        folder_id=folder_id,
                        defaults={
                            'parent_id': parent_id,
                            'name': folder_name,
                            'path': f"/{folder_name}",  # 簡易パス
                            'is_active': True
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to cache folder {folder_id}: {e}")

                # サブフォルダを取得
                try:
                    query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
                    page_token = None

                    while True:
                        results = self.service.files().list(
                            q=query,
                            fields="nextPageToken, files(id, name)",
                            pageSize=1000,
                            pageToken=page_token
                        ).execute()

                        subfolders = results.get('files', [])
                        for subfolder in subfolders:
                            queue.append((subfolder['id'], folder_id, subfolder['name']))

                        page_token = results.get('nextPageToken')
                        if not page_token:
                            break

                except Exception as e:
                    logger.error(f"Error listing subfolders of {folder_id}: {e}")
                    continue

            elapsed = time.time() - start_time
            logger.info(f"Built folder cache: {len(all_folder_ids)} folders in {elapsed:.2f}s")

            return all_folder_ids

        except Exception as e:
            logger.error(f"Error building folder cache: {e}")
            # フォールバック: 最低限ルートフォルダを返す
            return [root_folder_id]

    def invalidate_cache(self, root_folder_id: Optional[str] = None):
        """
        キャッシュを無効化

        Args:
            root_folder_id: 特定のルートフォルダのキャッシュのみ無効化（Noneなら全て）
        """
        try:
            if root_folder_id:
                FolderCache.objects.filter(folder_id=root_folder_id).update(is_active=False)
                logger.info(f"Invalidated cache for folder {root_folder_id}")
            else:
                FolderCache.objects.all().update(is_active=False)
                logger.info("Invalidated all folder caches")
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")


class BatchSearchService:
    """バッチ検索実行サービス"""

    def __init__(self, service):
        """
        Args:
            service: Google Drive API service instance
        """
        self.service = service
        self.batch_size = 100  # Google API制限

    def batch_search(self, folder_ids: List[str], search_conditions: str) -> List[Dict]:
        """
        バッチ検索を実行

        Args:
            folder_ids: 検索対象フォルダIDのリスト
            search_conditions: 検索条件（name contains 'keyword' など）

        Returns:
            検索結果のリスト
        """
        if not folder_ids:
            return []

        start_time = time.time()
        all_results = []

        # フォルダIDを100件ずつのチャンクに分割
        folder_chunks = [folder_ids[i:i+self.batch_size] for i in range(0, len(folder_ids), self.batch_size)]

        logger.info(f"Starting batch search across {len(folder_ids)} folders in {len(folder_chunks)} batches")

        for chunk_idx, chunk in enumerate(folder_chunks):
            try:
                chunk_results = self._execute_batch(chunk, search_conditions)
                all_results.extend(chunk_results)
                logger.debug(f"Batch {chunk_idx + 1}/{len(folder_chunks)}: found {len(chunk_results)} items")
            except Exception as e:
                logger.error(f"Error in batch {chunk_idx + 1}: {e}")
                continue

        elapsed = time.time() - start_time
        logger.info(f"Batch search completed: {len(all_results)} results in {elapsed:.2f}s")

        return all_results

    def _execute_batch(self, folder_ids: List[str], search_conditions: str) -> List[Dict]:
        """
        単一のバッチリクエストを実行

        Args:
            folder_ids: フォルダIDのリスト（最大100件）
            search_conditions: 検索条件

        Returns:
            検索結果のリスト
        """
        results = []
        batch = BatchHttpRequest()

        def callback(request_id, response, exception):
            """バッチリクエストのコールバック"""
            if exception:
                logger.warning(f"Search error in folder {request_id}: {exception}")
            else:
                files = response.get('files', [])
                results.extend(files)

        # バッチにリクエストを追加
        for folder_id in folder_ids:
            query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
            if search_conditions:
                query += f" and {search_conditions}"

            batch.add(
                self.service.files().list(
                    q=query,
                    fields="files(id, name, mimeType, webViewLink)",
                    pageSize=100
                ),
                callback=callback,
                request_id=folder_id
            )

        # バッチを実行
        batch.execute()

        return results
