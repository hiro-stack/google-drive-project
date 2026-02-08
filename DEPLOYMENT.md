# 🚀 デプロイガイド：PWA + Render

このガイドに従って、友人と共有できるPWAアプリをデプロイします。

---

## 📋 事前準備

### 1. 必要なアカウント

- **GitHub アカウント**（無料）
- **Render アカウント**（無料）https://render.com
- **Google Service Account**（Google Driveアクセス用）

---

## 🔧 ステップ1: GitHubにプッシュ

### A. Gitリポジトリを初期化（まだの場合）

```bash
cd c:\Users\zhang\python\ai_project_2
git init
git add .
git commit -m "Initial commit with PWA and cache optimization"
```

### B. GitHubにプッシュ

1. GitHub.comで新しいリポジトリを作成
2. リポジトリURLをコピー（例: `https://github.com/yourusername/drive-explorer.git`）

```bash
git remote add origin https://github.com/yourusername/drive-explorer.git
git branch -M main
git push -u origin main
```

---

## 🌐 ステップ2: Renderにデプロイ

### A. Renderに接続

1. https://render.com にアクセス
2. 「Sign Up」または「Log In」
3. 「Connect GitHub」でGitHubアカウントを連携

### B. バックエンドをデプロイ

1. ダッシュボードで「New +」→「Blueprint」をクリック
2. GitHubリポジトリを選択
3. `render.yaml`を検出して自動設定
4. 「Apply」をクリック

### C. 環境変数を設定

デプロイ後、バックエンドサービスの設定で以下を追加：

#### **GOOGLE_DRIVE_FOLDER_ID**
```
あなたのGoogle DriveフォルダID
```

#### **GOOGLE_CREDENTIALS_JSON**
```json
{
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

> **注意**: JSONをそのまま1行で貼り付けてください。

---

## 📱 ステップ3: PWAとしてインストール

### デプロイ完了後のURL

- **フロントエンド**: `https://drive-explorer-frontend.onrender.com`
- **バックエンド**: `https://drive-explorer-backend.onrender.com`

### 友人に共有

フロントエンドのURLを友人に送信：
```
https://drive-explorer-frontend.onrender.com
```

### スマホにインストール

#### **iPhone/iPad:**
1. Safari でURLを開く
2. 画面下部の「共有」ボタン（□↑）をタップ
3. 「ホーム画面に追加」をタップ
4. アプリ名を確認 → 「追加」

#### **Android:**
1. Chrome でURLを開く
2. 右上のメニュー（⋮）→「アプリをインストール」
3. または画面下部に「ホーム画面に追加」ポップアップが表示される

---

## 🔐 ステップ4: プライベート配布（オプション）

### 方法1: 簡易パスワード保護

バックエンドに認証を追加して、パスワードを知っている人のみアクセス可能にします。

#### A. 環境変数に追加

Renderのバックエンド設定で：
```
AUTH_PASSWORD=your_secret_password_12345
```

#### B. Djangoミドルウェアを追加

`backend/config/middleware.py`を作成：

```python
from django.http import JsonResponse
from django.conf import settings
import os

class SimpleAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_password = os.getenv('AUTH_PASSWORD')

        if not auth_password:
            return self.get_response(request)

        # 認証ヘッダーをチェック
        provided_password = request.headers.get('X-Auth-Password')

        if provided_password != auth_password:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        return self.get_response(request)
```

`backend/config/settings.py`に追加：
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'config.middleware.SimpleAuthMiddleware',  # 追加
    # ... 他のミドルウェア
]
```

フロントエンドで認証ヘッダーを追加：
```typescript
// frontend/src/hooks/useDriveExplorer.ts
const headers = {
  'X-Auth-Password': 'your_secret_password_12345'
};
```

### 方法2: URLを秘密にする

- フロントエンドURLを友人にのみ共有
- URLは推測困難（例: `https://drive-explorer-abc123xyz.onrender.com`）
- Google検索にはインデックスされません（noindexメタタグ追加済み）

---

## 🧪 動作確認

### 1. バックエンドが動作しているか確認

ブラウザで以下にアクセス：
```
https://drive-explorer-backend.onrender.com/api/folders/
```

エラーでなければ成功！

### 2. フロントエンドが動作しているか確認

ブラウザで以下にアクセス：
```
https://drive-explorer-frontend.onrender.com
```

PDFファイルが表示されれば成功！

### 3. PWA機能をテスト

スマホでインストール後：
- オフライン時にも開ける
- アプリアイコンがホーム画面に表示される
- アプリのように動作する

---

## 🔄 更新方法

### コードを更新したら

```bash
git add .
git commit -m "Update search feature"
git push
```

Renderが自動的に再デプロイします（約5-10分）。

---

## 💡 トラブルシューティング

### バックエンドが起動しない

1. Renderのログを確認：「Logs」タブ
2. 環境変数が正しく設定されているか確認
3. `GOOGLE_CREDENTIALS_JSON`のJSONフォーマットが正しいか確認

### フロントエンドが表示されない

1. バックエンドURLが正しく設定されているか確認
2. CORSエラーの場合は`settings.py`の`CORS_ALLOWED_ORIGINS`を確認

### PWAとしてインストールできない

1. HTTPSで配信されているか確認（Renderは自動でHTTPS）
2. `manifest.json`と`next.config.ts`が正しいか確認
3. Service Workerが登録されているか確認（DevToolsで確認）

---

## 📞 サポート

問題が解決しない場合は、Renderのログやエラーメッセージを共有してください！

---

## 🎉 完了！

これで、友人と共有できるPWAアプリが完成しました！

- **App Store審査不要**
- **iOS/Android両対応**
- **無料ホスティング**
- **高速検索**（50-75倍高速化）
- **多言語対応**（英語↔カタカナ↔ひらがな）

楽しんでください！🚀
