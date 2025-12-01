import csv
import re
import tkinter as tk
import os

# -------------------------------
# Utilities
# -------------------------------

def remove_diacritics(text):
    diacritics = re.compile(r'[\u064B-\u0652\u0653\u0654\u0655\u0670\u06D6-\u06ED]')
    return diacritics.sub('', text)

# Character-to-IPA map (taa marbuta handled by rules)
char_map = {
    'ا': 'aː', 'ب': 'b', 'ت': 't', 'ث': 'θ', 'ج': 'dʒ', 'ح': 'ħ', 'خ': 'x',
    'د': 'd', 'ذ': 'ð', 'ر': 'ɾ', 'ز': 'z', 'س': 's', 'ش': 'ʃ', 'ص': 'sˤ',
    'ض': 'dˤ', 'ط': 'tˤ', 'ظ': 'ðˤ', 'ع': 'ʕ', 'غ': 'ɣ', 'ف': 'f', 'ق': 'g',
    'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h', 'و': 'W', 'ي': 'j',
    'ى': 'a', 'ء': 'ʔ', 'أ': 'ʔə', 'إ': 'ʔɪ', 'ؤ': 'ʔʊ', 'ئ': 'ʔ',
    'ّ': 'ː', 'ة': 't'
}

# Sun letters in IPA onsets (multi-char clusters included)
SUN_ONSETS = ['tˤ','dˤ','sˤ','ðˤ', 't','θ','d','ð','ɾ','z','s','ʃ','l','n']
# Sort by length to prefer multi-char matches first
SUN_ONSETS.sort(key=len, reverse=True)

# Vowel set for sandhi check
vowels = ('a','e','i','o','u','ə','ʊ','ɪ','aː','iː','uː')

def map_chars(word):
    return ''.join(char_map.get(c, '') for c in word)

def collapse_doubles(ipa):
    consonant_class = r"[btdθdʒħxðɾzsʃsˤdˤtˤðˤʕɣfgklmnhwj]"
    return re.sub(rf"({consonant_class})\1", r"\1", ipa)

def tokenise(utterance):
    return re.findall(r'\w+|[^\w\s]', utterance, re.UNICODE)

# Helper: detect if a sun-onset starts at position pos; return (cluster, length) or (None, 0)
def detect_sun_onset(ipa, pos):
    for cl in SUN_ONSETS:
        if ipa[pos:].startswith(cl):
            return cl, len(cl)
    return None, 0

# -------------------------------
# Core rules (including stepwise article logic)
# -------------------------------

def apply_rules(ipa, word, prev_word_ipa=None, next_word=None):
    # Taa marbuta (ة): schwa sentence-final or before punctuation; [t] only if next starts with ال; else schwa
    if word.endswith('ة'):
        before_punct = (next_word in {',','،','.','!','?'} or next_word is None)
        if before_punct:
            ipa = re.sub(r't$', 'ə', ipa)
        elif next_word and isinstance(next_word, str) and next_word.startswith('ال'):
            ipa = re.sub(r't$', 't', ipa)
        else:
            ipa = re.sub(r't$', 'ə', ipa)

    # و: w if stand-alone or initial; uː mid/final
    if 'W' in ipa:
        if len(ipa) == 1:
            ipa = 'w'
        elif ipa.startswith('W'):
            ipa = ipa.replace('W','w',1)
        elif ipa.endswith('W'):
            ipa = ipa[:-1] + 'uː'
        else:
            ipa = ipa.replace('W','uː')

    # ي: jə standalone; j initial; iː mid/final
    if word == 'ي':
        ipa = 'jə'
    elif ipa.startswith('j'):
        ipa = ipa
    elif ipa.endswith('j'):
        ipa = ipa[:-1] + 'iː'
    else:
        ipa = ipa.replace('j','iː')

    # -------------------------------
    # STEP 1 — Normalize article forms to prefixes with explicit vowels
    # Ø → əl..., w → wəl..., j → jəl..., fɪ → fɪl..., bɪ → bɪl...
    # Note: ɪ replaces schwa for fɪ/bɪ
    # -------------------------------
    if ipa.startswith('aːl'):
        ipa = 'əl' + ipa[3:]          # aːlX → əlX
    elif ipa.startswith('waːl'):
        ipa = 'wəl' + ipa[4:]         # waːlX → wəlX
    elif ipa.startswith('jaːl'):
        ipa = 'jəl' + ipa[4:]         # jaːlX → jəlX
    # Cross-word or cliticized fi/bi → fɪl/bɪl
    elif ipa.startswith('fiːl'):
        ipa = 'fɪl' + ipa[4:]
    elif ipa.startswith('fiː'):
        ipa = 'fɪl' + ipa[3:]         # fiː + (assumed ال) → fɪl...
    elif ipa.startswith('biːl'):
        ipa = 'bɪl' + ipa[4:]
    elif ipa.startswith('biː'):
        ipa = 'bɪl' + ipa[3:]

    # -------------------------------
    # STEP 2 — Sun-letter assimilation
    # (PREFIX + ə/ɪ) + l + SUN → PREFIX + ə/ɪ + SUNː
    # Prefixes to consider after normalization:
    prefixes = ['əl','wəl','jəl','fɪl','bɪl']
    for pref in prefixes:
        if ipa.startswith(pref) and len(ipa) > len(pref):
            onset, L = detect_sun_onset(ipa, len(pref))  # onset immediately after 'l'
            if onset:
                # Build head: drop the 'l' in the prefix, keep its vowel
                if pref == 'əl':
                    head = 'ə'
                elif pref == 'wəl':
                    head = 'wə'
                elif pref == 'jəl':
                    head = 'jə'
                elif pref == 'fɪl':
                    head = 'fɪ'
                else:  # 'bɪl'
                    head = 'bɪ'
                rest = ipa[len(pref)+L:]
                ipa = head + onset + 'ː' + rest
                break  # only one prefix match per word

    # -------------------------------
    # STEP 3 — Sandhi after vowel-final previous word
    # Drop ONLY the schwa for Ø/w/j forms; fɪ/bɪ retain ɪ.
    # -------------------------------
    if prev_word_ipa and re.search(r'(?:a|e|i|o|u|ə|ʊ|ɪ|aː|iː|uː)$', prev_word_ipa):
        if ipa.startswith('əl'):          # l + MOON...
            ipa = 'l' + ipa[2:]
        elif ipa.startswith('wə'):
            ipa = 'w' + ipa[2:]           # drop schwa only
        elif ipa.startswith('jə'):
            ipa = 'j' + ipa[2:]
        elif ipa.startswith('ə'):
            ipa = ipa[1:]                 # drop leading schwa for assimilated əCː
        # fɪ/bɪ: do nothing — retain ɪ across all steps

    # Hiatus: insert ʔ if vowel-final word precedes vowel-initial word
    if prev_word_ipa and re.search(r'[aeiouəʊɪ]$', prev_word_ipa) and re.match(r'^[aeiouəʊɪ]', ipa):
        ipa = 'ʔ' + ipa

    # Collapse double consonants (preserve ː)
    ipa = collapse_doubles(ipa)

    return ipa

def transcribe_fallback(word, prev_word_ipa=None, next_word=None):
    raw_ipa = map_chars(word)
    return apply_rules(raw_ipa, word, prev_word_ipa, next_word)

# -------------------------------
# Transcriber class
# -------------------------------

class HijaziTranscriber:
    def __init__(self, lexicon_path):
        self.lexicon = self.load_lexicon(lexicon_path)

    def load_lexicon(self, path):
        lexicon = {}
        if not os.path.exists(path):
            return lexicon  # safe fallback
        with open(path, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) < 2:
                    continue
                orth, ipa = row[:2]
                lexicon[orth.strip()] = ipa.strip()
        return lexicon

    def transliterate(self, utterance, show_fallback=False):
        words = tokenise(utterance.strip())
        ipa_sequence = []
        prev_word_ipa = None

        for i, word in enumerate(words):
            clean_word = remove_diacritics(word)
            next_word = words[i+1] if i+1 < len(words) else None

            if clean_word in self.lexicon:
                ipa = self.lexicon[clean_word]
                ipa = apply_rules(ipa, clean_word, prev_word_ipa, next_word)
            else:
                ipa = transcribe_fallback(clean_word, prev_word_ipa, next_word)
                if show_fallback and re.match(r'^\w+$', word):
                    ipa += ' [F]'

            # Cross-word assimilation: n + l → lː (delete final n, lengthen following l)
            if prev_word_ipa and prev_word_ipa.endswith('n') and ipa.startswith('l'):
                prev_word_ipa = prev_word_ipa[:-1]
                ipa = 'lː' + ipa[1:]
                if ipa_sequence:
                    ipa_sequence[-1] = prev_word_ipa

            ipa_sequence.append(ipa)
            prev_word_ipa = ipa

        return ' '.join(ipa_sequence)

# -------------------------------
# GUI
# -------------------------------

def launch_gui():
    transcriber = HijaziTranscriber('lexicon.csv')

    def on_transcribe():
        input_text = input_box.get("1.0", tk.END).strip()
        show_fallback = fallback_var.get()
        ipa = transcriber.transliterate(input_text, show_fallback)
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, ipa)

    root = tk.Tk()
    root.title("Hijazi IPA Pad")

    tk.Label(root, text="Arabic Input").pack()
    input_box = tk.Text(root, height=4, width=50)
    input_box.pack()

    fallback_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Show fallback tags", variable=fallback_var).pack()

    tk.Button(root, text="Transcribe", command=on_transcribe).pack()

    tk.Label(root, text="IPA Output").pack()
    output_box = tk.Text(root, height=4, width=50)
    output_box.pack()

    root.mainloop()

if __name__ == "__main__":
    launch_gui()