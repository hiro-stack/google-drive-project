#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# マイグレーションを実行
python manage.py migrate --noinput

# 静的ファイルを収集
python manage.py collectstatic --noinput --clear
