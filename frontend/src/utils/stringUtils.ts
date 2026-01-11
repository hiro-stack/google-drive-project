export function normalizeQuery(text: string): string {
  if (!text) return '';
  
  return text
    .replace(/[。、．・!！?？]/g, '')         // Remove punctuation
    .replace(/ー/g, '')                       // Remove prolonged sound marks
    .replace(/\s+/g, '')                      // Remove whitespace (Note: this disables space-separated AND search)
    .replace(/[ぁ-ん]/g, c =>                 // Convert Hiragana to Katakana
      String.fromCharCode(c.charCodeAt(0) + 0x60)
    )
    .toLowerCase();                          // Convert to lowercase
}
