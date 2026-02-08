import re

# ライブラリがインストールされていない場合でもサーバーが落ちないようにする
try:
    import jaconv
    HAS_JACONV = True
except ImportError:
    HAS_JACONV = False

try:
    import romkan
    HAS_ROMKAN = True
except ImportError:
    HAS_ROMKAN = False

HAS_NLP_LIBS = HAS_JACONV and HAS_ROMKAN

if HAS_JACONV and HAS_ROMKAN:
    print("[OK] jaconv and romkan successfully imported. Algorithmic expansion ENABLED.")
elif HAS_JACONV:
    print("[WARNING] Only jaconv imported. romkan not available. Limited expansion enabled.")
else:
    print("[WARNING] jaconv and/or romkan not found. Algorithmic expansion DISABLED.")

# キャッシュモデルをインポート（循環インポート回避のため遅延インポート）
try:
    from folders.models import SynonymCache
    HAS_CACHE = True
except ImportError:
    HAS_CACHE = False
    print("⚠️ Warning: SynonymCache model not available")

class SynonymDict:
    def __init__(self):
        # 拡張類義語/表記ゆれ辞書（双方向マッピング）
        self.dictionary = {
            # 既存のエントリ
            'happy': ['happy', 'ハッピー', 'はっぴー', 'happier', 'unhappy', '幸せ', 'しあわせ'],
            'ハッピー': ['happy', 'ハッピー', 'はっぴー', 'happier', 'unhappy', '幸せ', 'しあわせ'],
            'はっぴー': ['happy', 'ハッピー', 'はっぴー', 'happier', 'unhappy', '幸せ', 'しあわせ'],
            'birthday': ['birthday', 'バースデー', 'バースデイ', 'ばーすでー', '誕生日', 'たんじょうび'],
            'バースデー': ['birthday', 'バースデー', 'バースデイ', 'ばーすでー', '誕生日', 'たんじょうび'],
            'バースデイ': ['birthday', 'バースデー', 'バースデイ', 'ばーすでー', '誕生日', 'たんじょうび'],
            'pdf': ['pdf', 'document', '資料', 'しりょう'],
            'music': ['music', '音楽', 'おんがく', 'score', '楽譜', 'がくふ'],
            '音楽': ['music', '音楽', 'おんがく', 'score', '楽譜', 'がくふ'],
            '楽譜': ['music', '音楽', 'おんがく', 'score', '楽譜', 'がくふ'],
            'hymn': ['hymn', 'ヒム', 'ひむ', '賛美歌', 'さんびか', '聖歌', 'せいか'],
            '賛美歌': ['hymn', 'ヒム', 'ひむ', '賛美歌', 'さんびか', '聖歌', 'せいか'],

            # 新規追加：教会/音楽関連
            'praise': ['praise', 'プレイズ', 'ぷれいず', '賛美', 'さんび', 'worship', 'ワーシップ'],
            'プレイズ': ['praise', 'プレイズ', 'ぷれいず', '賛美', 'さんび', 'worship', 'ワーシップ'],
            '賛美': ['praise', 'プレイズ', 'ぷれいず', '賛美', 'さんび', 'worship', 'ワーシップ'],

            'worship': ['worship', 'ワーシップ', 'わーしっぷ', '礼拝', 'れいはい', 'praise', 'プレイズ'],
            'ワーシップ': ['worship', 'ワーシップ', 'わーしっぷ', '礼拝', 'れいはい', 'praise', 'プレイズ'],
            '礼拝': ['worship', 'ワーシップ', 'わーしっぷ', '礼拝', 'れいはい'],

            'song': ['song', 'ソング', 'そんぐ', '歌', 'うた', '曲', 'きょく'],
            'ソング': ['song', 'ソング', 'そんぐ', '歌', 'うた', '曲', 'きょく'],
            '歌': ['song', 'ソング', 'そんぐ', '歌', 'うた', '曲', 'きょく'],
            '曲': ['song', 'ソング', 'そんぐ', '歌', 'うた', '曲', 'きょく'],

            'christmas': ['christmas', 'クリスマス', 'くりすます', 'xmas', 'Xmas', '聖誕', 'せいたん', 'クリスマス'],
            'クリスマス': ['christmas', 'クリスマス', 'くりすます', 'xmas', 'Xmas', '聖誕', 'せいたん'],
            'xmas': ['christmas', 'クリスマス', 'くりすます', 'xmas', 'Xmas', '聖誕', 'せいたん'],

            'easter': ['easter', 'イースター', 'いーすたー', '復活祭', 'ふっかつさい', 'イースター'],
            'イースター': ['easter', 'イースター', 'いーすたー', '復活祭', 'ふっかつさい'],
            '復活祭': ['easter', 'イースター', 'いーすたー', '復活祭', 'ふっかつさい'],

            'hallelujah': ['hallelujah', 'ハレルヤ', 'はれるや', 'alleluia', 'アレルヤ', 'あれるや'],
            'ハレルヤ': ['hallelujah', 'ハレルヤ', 'はれるや', 'alleluia', 'アレルヤ', 'あれるや'],
            'alleluia': ['hallelujah', 'ハレルヤ', 'はれるや', 'alleluia', 'アレルヤ', 'あれるや'],

            'prayer': ['prayer', 'プレイヤー', 'ぷれいやー', '祈り', 'いのり', '祈祷', 'きとう'],
            'プレイヤー': ['prayer', 'プレイヤー', 'ぷれいやー', '祈り', 'いのり'],
            '祈り': ['prayer', 'プレイヤー', 'ぷれいやー', '祈り', 'いのり'],

            'bible': ['bible', 'バイブル', 'ばいぶる', '聖書', 'せいしょ'],
            'バイブル': ['bible', 'バイブル', 'ばいぶる', '聖書', 'せいしょ'],
            '聖書': ['bible', 'バイブル', 'ばいぶる', '聖書', 'せいしょ'],

            'church': ['church', 'チャーチ', 'ちゃーち', '教会', 'きょうかい'],
            'チャーチ': ['church', 'チャーチ', 'ちゃーち', '教会', 'きょうかい'],
            '教会': ['church', 'チャーチ', 'ちゃーち', '教会', 'きょうかい'],

            'god': ['god', 'ゴッド', 'ごっど', '神', 'かみ', '主', 'しゅ'],
            'ゴッド': ['god', 'ゴッド', 'ごっど', '神', 'かみ'],
            '神': ['god', 'ゴッド', 'ごっど', '神', 'かみ', '主', 'しゅ'],
            '主': ['god', 'ゴッド', 'ごっど', '神', 'かみ', '主', 'しゅ'],

            'jesus': ['jesus', 'ジーザス', 'じーざす', 'イエス', 'いえす', 'キリスト', 'きりすと'],
            'ジーザス': ['jesus', 'ジーザス', 'じーざす', 'イエス', 'いえす'],
            'イエス': ['jesus', 'ジーザス', 'じーざす', 'イエス', 'いえす', 'キリスト', 'きりすと'],
            'キリスト': ['jesus', 'ジーザス', 'じーざす', 'イエス', 'いえす', 'キリスト', 'きりすと'],

            'grace': ['grace', 'グレース', 'ぐれーす', '恵み', 'めぐみ'],
            'グレース': ['grace', 'グレース', 'ぐれーす', '恵み', 'めぐみ'],
            '恵み': ['grace', 'グレース', 'ぐれーす', '恵み', 'めぐみ'],

            'love': ['love', 'ラブ', 'らぶ', '愛', 'あい'],
            'ラブ': ['love', 'ラブ', 'らぶ', '愛', 'あい'],
            '愛': ['love', 'ラブ', 'らぶ', '愛', 'あい'],

            'peace': ['peace', 'ピース', 'ぴーす', '平和', 'へいわ', '平安', 'へいあん'],
            'ピース': ['peace', 'ピース', 'ぴーす', '平和', 'へいわ'],
            '平和': ['peace', 'ピース', 'ぴーす', '平和', 'へいわ', '平安', 'へいあん'],

            'spirit': ['spirit', 'スピリット', 'すぴりっと', '霊', 'れい', '御霊', 'みたま'],
            'スピリット': ['spirit', 'スピリット', 'すぴりっと', '霊', 'れい'],
            '霊': ['spirit', 'スピリット', 'すぴりっと', '霊', 'れい', '御霊', 'みたま'],
        }

    def normalize(self, text):
        """
        簡易正規化
        """
        if not text:
            return ""
        
        # ライブラリがある場合のみ高度な正規化を行う
        if HAS_JACONV:
            try:
                # 全角英数を半角に、半角カタカナを全角に統一
                text = jaconv.z2h(text, kana=False, digit=True, ascii=True)
                text = jaconv.h2z(text, kana=True, digit=False, ascii=False)
            except Exception:
                pass
                
        return text.lower().strip()

    def get_synonyms(self, word):
        """
        単語を受け取り、類義語リスト（アルゴリズム拡張含む）を返す
        キャッシュを使用してパフォーマンス向上
        """
        if not word:
            return []

        # キャッシュから取得を試みる
        if HAS_CACHE:
            try:
                cached = SynonymCache.objects.get(word=word)
                print(f"[CACHE HIT] for '{word}'")
                return cached.synonyms_json
            except SynonymCache.DoesNotExist:
                print(f"[CACHE MISS] for '{word}', generating...")
            except Exception as e:
                print(f"[WARNING] Cache error for '{word}': {e}")

        print(f"DEBUG: get_synonyms called with word='{word}', HAS_NLP_LIBS={HAS_NLP_LIBS}")

        synonyms = set()
        synonyms.add(word)

        # 1. 正規化して追加
        norm_word = self.normalize(word)
        synonyms.add(norm_word)

        # 2. 辞書ルックアップ
        if norm_word in self.dictionary:
            synonyms.update(self.dictionary[norm_word])

        # 3. アルゴリズム的拡張 (ライブラリがある場合のみ)
        if HAS_JACONV:
            try:
                # A. ひらがな ⇔ カタカナ
                hira = jaconv.kata2hira(norm_word)
                kata = jaconv.hira2kata(norm_word)
                synonyms.add(hira)
                synonyms.add(kata)
            except Exception as e:
                print(f"[WARNING] Conversion error for '{word}': {e}")

        if HAS_ROMKAN:
            try:
                # B. ローマ字 → カタカナ/ひらがな (入力がアルファベットの場合)
                if re.match(r'^[a-zA-Z]+$', norm_word):
                    converted_kata = romkan.to_katakana(norm_word)
                    converted_hira = romkan.to_hiragana(norm_word)
                    synonyms.add(converted_kata)
                    synonyms.add(converted_hira)
            except Exception as e:
                print(f"[WARNING] Romkan conversion error for '{word}': {e}")

        result = list(synonyms)
        print(f"DEBUG: get_synonyms result for '{word}': {result}")

        # キャッシュに保存
        if HAS_CACHE:
            try:
                SynonymCache.objects.create(word=word, synonyms_json=result)
                print(f"[CACHED] synonyms for '{word}'")
            except Exception as e:
                # キャッシュ失敗は検索を妨げない
                print(f"[WARNING] Failed to cache '{word}': {e}")

        return result

synonym_dict = SynonymDict()
