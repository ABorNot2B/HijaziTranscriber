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

# Superior character-to-IPA map (taa marbuta handled by rules)
char_map = {
    'ا': 'aː', 'ب': 'b', 'ت': 't', 'ث': 'θ', 'ج': 'dʒ', 'ح': 'ħ', 'خ': 'x',
    'د': 'd', 'ذ': 'ð', 'ر': 'ɾ', 'ز': 'z', 'س': 's', 'ش': 'ʃ', 'ص': 'sˤ',
    'ض': 'dˤ', 'ط': 'tˤ', 'ظ': 'ðˤ', 'ع': 'ʕ', 'غ': 'ɣ', 'ف': 'f', 'ق': 'g',
    'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h', 'و': 'W', 'ي': 'j',
    'ى': 'a', 'ء': 'ʔ', 'أ': 'ʔə', 'إ': 'ʔɪ', 'ؤ': 'ʔʊ', 'ئ': 'ʔ',
    'ّ': 'ː', 'ة': 't'
}

sun_letters = {'ت','ث','د','ذ','ر','ز','س','ش','ص','ض','ط','ظ','ل','ن'}
vowels = ('a','e','i','o','u','ə','ʊ','ɪ','aː','iː','uː')

def map_chars(word):
    return ''.join(char_map.get(c, '') for c in word)

def collapse_doubles(ipa):
    consonant_class = r"[btdθdʒħxðɾzsʃsˤdˤtˤðˤʕɣfgklmnhwj]"
    return re.sub(rf"({consonant_class})\1", r"\1", ipa)

def tokenise(utterance):
    return re.findall(r'\w+|[^\w\s]', utterance, re.UNICODE)

# -------------------------------
# Core rules
# -------------------------------

def apply_rules(ipa, word, prev_word_ipa=None, next_word=None):
    # Taa marbuta
    if word.endswith('ة'):
        before_punct = (next_word in {',','،','.','!','?'} or next_word is None)
        if before_punct:
            ipa = re.sub(r't$', 'ə', ipa)
        elif next_word and isinstance(next_word,str) and next_word.startswith('ال'):
            ipa = re.sub(r't$', 't', ipa)
        else:
            ipa = re.sub(r't$', 'ə', ipa)

    # و
    if 'W' in ipa:
        if len(ipa) == 1:
            ipa = 'w'
        elif ipa.startswith('W'):
            ipa = ipa.replace('W','w',1)
        elif ipa.endswith('W'):
            ipa = ipa[:-1] + 'uː'
        else:
            ipa = ipa.replace('W','uː')

    # ي
    if word == 'ي':
        ipa = 'jə'
    elif ipa.startswith('j'):
        ipa = ipa
    elif ipa.endswith('j'):
        ipa = ipa[:-1] + 'iː'
    else:
        ipa = ipa.replace('j','iː')

    # Definite article normalization
    if ipa.startswith('aːl'):
        ipa = ipa.replace('aːl','əl',1)

    # Sun-letter assimilation
    for prefix in ['əl','waːl','jaːl']:
        if ipa.startswith(prefix) and len(ipa) > len(prefix):
            nxt = ipa[len(prefix)]
            if nxt in sun_letters:
                ipa = 'ə' + nxt + 'ː' + ipa[len(prefix)+1:]

    # Moon letters
    if ipa.startswith('əl') and len(ipa) > 2 and ipa[2] not in sun_letters:
        if prev_word_ipa and prev_word_ipa.endswith(vowels):
            ipa = 'l' + ipa[2:]  # schwa drops if preceded by vowel
        # else: keep schwa + l

    # No hiatus
    if prev_word_ipa and re.search(r'[aeiouəʊɪ]$', prev_word_ipa) and re.match(r'^[aeiouəʊɪ]', ipa):
        ipa = 'ʔ' + ipa

    # Collapse doubles
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
            return lexicon  # safe fallback if file missing
        with open(path, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) < 2: continue
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

            # Cross-word assimilation: n + l → lː
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