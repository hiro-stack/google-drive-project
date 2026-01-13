import jaconv
import romkan
import re

class SynonymDict:
    def __init__(self):
        # 簡易類義語/表記ゆれ辞書
        # キー: 正規化された単語（小文字）
        # 値: 類義語リスト
        self.dictionary = {
            'happy': ['happy', 'ハッピー', 'happier', 'unhappy', '幸せ'],
            'ハッピー': ['happy', 'ハッピー', 'happier', 'unhappy', '幸せ'],
            'birthday': ['birthday', 'バースデー', 'バースデイ', '誕生日'],
            'バースデー': ['birthday', 'バースデー', 'バースデイ', '誕生日'],
            'pdf': ['pdf', 'document', '資料'],
            'music': ['music', '音楽', 'score', '楽譜'],
            '楽譜': ['music', '音楽', 'score', '楽譜'],
            'hymn': ['hymn', '賛美歌', '聖歌'],
            '賛美歌': ['hymn', '賛美歌', '聖歌'],
        }

    def normalize(self, text):
        """
        簡易正規化: 小文字変換、全角・半角スペース統一など
        """
        if not text:
            return ""
        # 全角英数を半角に、半角カタカナを全角に統一
        text = jaconv.z2h(text, kana=False, digit=True, ascii=True) # 全角英数→半角
        text = jaconv.h2z(text, kana=True, digit=False, ascii=False) # 半角カナ→全角
        return text.lower().strip()

    def get_synonyms(self, word):
        """
        単語を受け取り、類義語リスト（アルゴリズム拡張含む）を返す
        """
        if not word:
            return []
            
        synonyms = set()
        synonyms.add(word)
        
        # 1. 正規化して追加
        norm_word = self.normalize(word)
        synonyms.add(norm_word)
        
        # 2. 辞書ルックアップ
        if norm_word in self.dictionary:
            synonyms.update(self.dictionary[norm_word])

        # 3. アルゴリズム的拡張 (Algorithmic Expansion)
        
        # A. ひらがな ⇔ カタカナ
        hira = jaconv.kata2hira(norm_word)
        kata = jaconv.hira2kata(norm_word)
        synonyms.add(hira)
        synonyms.add(kata)
        
        # B. ローマ字 → カタカナ/ひらがな (入力がアルファベットの場合)
        if re.match(r'^[a-zA-Z]+$', norm_word):
            try:
                # romkanライブラリで変換 (例: "sushi" -> "スシ")
                converted_kata = romkan.to_katakana(norm_word)
                converted_hira = romkan.to_hiragana(norm_word)
                synonyms.add(converted_kata)
                synonyms.add(converted_hira)
            except:
                pass

        # C. カタカナ/ひらがな → ローマ字 (逆変換は文脈依存で難しいが、romkanはある程度可能)
        # 今回は誤爆を防ぐため、ローマ字への逆変換は行わない、もしくは主要なものだけに限定。

        return list(synonyms) # 重複排除してリスト化

synonym_dict = SynonymDict()
