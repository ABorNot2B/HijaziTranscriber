import csv
import re
import tkinter as tk

# Remove Arabic diacritics
def remove_diacritics(text):
    diacritics = re.compile(r'[\u064B-\u0652\u0670\u06D6-\u06ED]')
    return diacritics.sub('', text)

# 1:1 character-to-IPA mapping
char_map = {
    'ا': 'aː', 'ب': 'b', 'ت': 't', 'ث': 't', 'ج': 'd͡ʒ', 'ح': 'ħ', 'خ': 'x',
    'د': 'd', 'ذ': 'd', 'ر': 'ɾ', 'ز': 'z', 'س': 's', 'ش': 'ʃ', 'ص': 'sˤ',
    'ض': 'dˤ', 'ط': 'tˤ', 'ظ': 'ðˤ', 'ع': 'ʕ', 'غ': 'ɣ', 'ف': 'f', 'ق': 'g',
    'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h', 'و': 'uː', 'ي': 'iː',
    'ى': 'ə', 'ء': 'ʔ', 'أ': 'ʔ', 'إ': 'ʔɪ', 'ؤ': 'ʔʊ', 'ئ': 'ʔə', 'ّ': 'ː'
}

sun_letters = {'ت','ث','د','ذ','ر','ز','س','ش','ص','ض','ط','ظ','ل','ن'}

def map_chars(word):
    return ''.join(char_map.get(c, '[UNK]') for c in word)

def apply_rules(ipa, word):
    if word.endswith('ة'):
        ipa = re.sub('t$', 'ə', ipa)
    ipa = re.sub(r'^wː', 'w', ipa)
    ipa = ipa.replace('aːl', 'əl')
    if ipa.startswith('əl') and len(ipa) > 2 and ipa[2] in sun_letters:
        ipa = 'ə' + ipa[2] + 'ː' + ipa[3:]
    ipa = re.sub(r'^(uː)$', 'w', ipa)
    ipa = re.sub(r'^uː(?=\W|$)', 'w', ipa)
    ipa = re.sub(r'^(iː)$', 'je', ipa)
    ipa = re.sub(r'^iː(?=\W|$)', 'je', ipa)
    return ipa

def transcribe_fallback(word):
    raw_ipa = map_chars(word)
    return apply_rules(raw_ipa, word)

class HijaziTranscriber:
    def __init__(self, lexicon_path):
        self.lexicon = self.load_lexicon(lexicon_path)

    def load_lexicon(self, path):
        lexicon = {}
        with open(path, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                orth, ipa = row
                lexicon[orth.strip()] = ipa.strip()
        return lexicon

    def transliterate(self, utterance, show_fallback=False):
        words = utterance.strip().split()
        ipa_sequence = []
        for word in words:
            clean_word = remove_diacritics(word)
            if clean_word in self.lexicon:
                ipa = self.lexicon[clean_word]
            else:
                ipa = transcribe_fallback(clean_word)
                if show_fallback:
                    ipa += ' [F]'
            ipa_sequence.append(ipa)
        return ' '.join(ipa_sequence)

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