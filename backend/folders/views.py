from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import time
from search.synonyms import synonym_dict
from .cache_service import FolderCacheService, BatchSearchService

class FolderListView(APIView):
    def get(self, request):
        # Use query param 'folder_id' if provided, otherwise default to env var
        folder_id = request.query_params.get('folder_id') or settings.GOOGLE_DRIVE_FOLDER_ID
        
        try:
            # 優先: 環境変数からJSON文字列を読み込む（デプロイ環境用）
            json_creds = os.environ.get('GOOGLE_CREDENTIALS_JSON')
            
            if json_creds:
                import json
                info = json.loads(json_creds)
                creds = service_account.Credentials.from_service_account_info(
                    info, scopes=['https://www.googleapis.com/auth/drive.metadata.readonly']
                )
            else:
                # フォールバック: ローカルファイルから読み込む
                creds_file = settings.GOOGLE_SERVICE_ACCOUNT_FILE
                
                # Determine absolute path for creds file if it's relative
                if creds_file and not os.path.isabs(creds_file):
                    creds_path = os.path.join(settings.BASE_DIR, creds_file)
                else:
                    creds_path = creds_file

                if not creds_path or not os.path.exists(creds_path):
                    return Response(
                        {"error": "Service account file not found. Please ensure 'service_account.json' is present in the backend root or set GOOGLE_CREDENTIALS_JSON environment variable."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                creds = service_account.Credentials.from_service_account_file(
                    creds_path, scopes=['https://www.googleapis.com/auth/drive.metadata.readonly']
                )

            service = build('drive', 'v3', credentials=creds)
            
            query_text = request.query_params.get("query")

            if query_text:
                # バッチ検索モード
                try:
                    start_time = time.time()

                    # 1. キャッシュサービスとバッチ検索サービスの初期化
                    cache_service = FolderCacheService(service)
                    batch_search_service = BatchSearchService(service)

                    # 2. 全フォルダIDを取得（キャッシュから、または再構築）
                    cache_start = time.time()
                    all_folder_ids = cache_service.get_all_folder_ids(folder_id)
                    cache_time = time.time() - cache_start
                    print(f"[OK] Cache lookup: {len(all_folder_ids)} folders in {cache_time:.2f}s")

                    # 3. 検索クエリの準備（シノニム展開）
                    keywords = query_text.replace('　', ' ').split()
                    final_query_parts = []

                    for keyword in keywords:
                        synonyms = synonym_dict.get_synonyms(keyword)

                        synonym_parts = []
                        for syn in synonyms:
                            safe_syn = syn.replace("'", "\\'")
                            synonym_parts.append(f"name contains '{safe_syn}'")

                        if synonym_parts:
                            if len(synonym_parts) > 1:
                                joined_or = " or ".join(synonym_parts)
                                final_query_parts.append(f"({joined_or})")
                            else:
                                final_query_parts.append(synonym_parts[0])

                    name_conditions = " and ".join(final_query_parts)
                    print(f"[SEARCH] conditions: {name_conditions}")

                    # 4. バッチ検索実行
                    search_start = time.time()
                    all_items = batch_search_service.batch_search(all_folder_ids, name_conditions)
                    search_time = time.time() - search_start

                    total_time = time.time() - start_time
                    print(f"[OK] Search completed: {len(all_items)} results in {search_time:.2f}s (total: {total_time:.2f}s)")

                    return Response(all_items)

                except Exception as e:
                    print(f"[ERROR] Error in batch search: {e}")
                    return Response({"error": str(e)}, status=500)

            # Normal navigation mode (current folder only)
            query = f"'{folder_id}' in parents and trashed = false"
            
            results = service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, webViewLink)",
                orderBy="folder,name"
            ).execute()
            
            items = results.get('files', [])
            
            return Response(items)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CacheRefreshView(APIView):
    """キャッシュを手動で更新するエンドポイント"""

    def post(self, request):
        try:
            folder_id = request.data.get('folder_id') or settings.GOOGLE_DRIVE_FOLDER_ID

            # Google Drive API認証
            json_creds = os.environ.get('GOOGLE_CREDENTIALS_JSON')

            if json_creds:
                import json
                info = json.loads(json_creds)
                creds = service_account.Credentials.from_service_account_info(
                    info, scopes=['https://www.googleapis.com/auth/drive.metadata.readonly']
                )
            else:
                creds_file = settings.GOOGLE_SERVICE_ACCOUNT_FILE
                if creds_file and not os.path.isabs(creds_file):
                    creds_path = os.path.join(settings.BASE_DIR, creds_file)
                else:
                    creds_path = creds_file

                if not creds_path or not os.path.exists(creds_path):
                    return Response(
                        {"error": "Service account file not found"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                creds = service_account.Credentials.from_service_account_file(
                    creds_path, scopes=['https://www.googleapis.com/auth/drive.metadata.readonly']
                )

            service = build('drive', 'v3', credentials=creds)

            # キャッシュサービス初期化
            cache_service = FolderCacheService(service)

            # キャッシュ無効化と再構築
            cache_service.invalidate_cache(folder_id)
            start_time = time.time()
            folder_ids = cache_service.build_folder_cache(folder_id)
            elapsed = time.time() - start_time

            return Response({
                "status": "success",
                "message": f"Cache refreshed for folder {folder_id}",
                "folder_count": len(folder_ids),
                "elapsed_seconds": round(elapsed, 2)
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
