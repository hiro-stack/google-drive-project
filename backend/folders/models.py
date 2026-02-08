from django.db import models


class FolderCache(models.Model):
    """フォルダ構造のキャッシュ"""
    folder_id = models.CharField(max_length=255, primary_key=True)
    parent_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    name = models.CharField(max_length=512)
    path = models.TextField()  # 表示用の完全パス
    last_updated = models.DateTimeField(auto_now=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'folder_cache'

    def __str__(self):
        return f"{self.name} ({self.folder_id})"


class SearchResultCache(models.Model):
    """検索結果のキャッシュ"""
    query_hash = models.CharField(max_length=64, primary_key=True)
    query_text = models.TextField()
    results_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'search_result_cache'

    def __str__(self):
        return f"Cache for: {self.query_text[:50]}"


class SynonymCache(models.Model):
    """シノニム検索のキャッシュ"""
    word = models.CharField(max_length=255, primary_key=True)
    synonyms_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'synonym_cache'

    def __str__(self):
        return f"Synonyms for: {self.word}"
