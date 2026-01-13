class SynonymDict:
    def __init__(self):
        # 簡易類義語/表記ゆれ辞書
        # キー: 正規化された単語（小文字）
        # 値: 類義語リスト
        self.dictionary = {
            'happy': ['happy', 'ハッピー', 'happier', 'unhappy'],
            'ハッピー': ['happy', 'ハッピー', 'happier', 'unhappy'],
            'birthday': ['birthday', 'バースデー', 'バースデイ'],
            'バースデー': ['birthday', 'バースデー', 'バースデイ'],
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
        # 全角英数を半角にしてもいいが、今回は小文字化のみ
        return text.lower().strip()

    def get_synonyms(self, word):
        """
        単語を受け取り、類義語リスト（自分自身含む）を返す
        """
        norm_word = self.normalize(word)
        
        # 辞書にあればそれを返す
        if norm_word in self.dictionary:
            return self.dictionary[norm_word]
        
        # 辞書になくても、自分自身は返す
        # ここでアルゴリズム的な変換（ローマ字→カタカナ）を入れることも可能だが、
        # 安定性重視で今回は辞書のみ。
        return [word]

synonym_dict = SynonymDict()
