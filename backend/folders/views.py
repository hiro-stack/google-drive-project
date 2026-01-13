from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from search.synonyms import synonym_dict

def list_all_folder_ids(service, parent_id):
    """Recursive function to get all subfolder IDs."""
    folder_ids = [parent_id]
    query = f"'{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    
    page_token = None
    while True:
        try:
            results = service.files().list(
                q=query, 
                fields="nextPageToken, files(id)",
                pageSize=1000,
                pageToken=page_token
            ).execute()
            
            subfolders = results.get('files', [])
            for folder in subfolders:
                folder_ids.extend(list_all_folder_ids(service, folder['id']))
                
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        except Exception as e:
            print(f"Error accessing folder {parent_id}: {e}")
            break
            
    return folder_ids

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
                # Recursive search mode
                try:
                    # 1. Get all folder IDs (recursive)
                    all_folder_ids = list_all_folder_ids(service, folder_id)
                    
                    # 2. Prepare search query (keywords AND logic, synonyms OR logic)
                    keywords = query_text.replace('　', ' ').split()
                    final_query_parts = []
                    
                    for keyword in keywords:
                        # 類義語を取得
                        synonyms = synonym_dict.get_synonyms(keyword)
                        
                        # 類義語ごとのクエリ (OR条件)
                        # name contains 'A' or name contains 'B'
                        synonym_parts = []
                        for syn in synonyms:
                            safe_syn = syn.replace("'", "\\'")
                            synonym_parts.append(f"name contains '{safe_syn}'")
                        
                        if synonym_parts:
                            # 複数の類義語がある場合はカッコで囲む
                            if len(synonym_parts) > 1:
                                joined_or = " or ".join(synonym_parts)
                                final_query_parts.append(f"({joined_or})")
                            else:
                                final_query_parts.append(synonym_parts[0])
                                
                    name_conditions = " and ".join(final_query_parts)
                    print(f"DEBUG: Search Query Conditions: {name_conditions}")

                    all_items = []
                    
                    # 3. Search in each folder
                    for fid in all_folder_ids:
                        # Searching for PDF files as per requirement
                        query = f"'{fid}' in parents and mimeType = 'application/pdf' and trashed = false"
                        if name_conditions:
                            query += f" and {name_conditions}"
                        
                        try:
                            results = service.files().list(
                                q=query,
                                fields="files(id, name, mimeType, webViewLink)",
                                pageSize=100
                            ).execute()
                            all_items.extend(results.get("files", []))
                        except Exception as e:
                            print(f"Error searching in subfolder {fid}: {e}")
                            continue

                    return Response(all_items)
                    
                except Exception as e:
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
