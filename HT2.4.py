import csv
import re
import tkinter as tk
import os

def remove_diacritics(text):
    d = re.compile(r'[\u064B-\u0652\u0653-\u0655\u0670\u06D6-\u06ED]')
    return d.sub('', text)

char_map = {
    'ا': 'aː','ب': 'b','ت': 't','ث': 'θ','ج': 'dʒ','ح': 'ħ','خ': 'x',
    'د': 'd','ذ': 'ð','ر': 'ɾ','ز': 'z','س': 's','ش': 'ʃ','ص': 'sˤ',
    'ض': 'dˤ','ط': 'tˤ','ظ': 'ðˤ','ع': 'ʕ','غ': 'ɣ','ف': 'f','ق': 'g',
    'ك': 'k','ل': 'l','م': 'm','ن': 'n','ه': 'h','و': 'w','ي': 'j',
    'ى': 'a','ء': 'ʔ','أ': 'ʔə','إ': 'ʔɪ','ؤ': 'ʔʊ','ئ': 'ʔ',
    'ّ': 'ː','ة': 't'
}

SUN_ONSETS = ['tˤ','dˤ','sˤ','ðˤ','t','θ','d','ð','ɾ','z','s','ʃ','l','n']
SUN_ONSETS.sort(key=len, reverse=True)

def map_chars(word):
    return ''.join(char_map.get(c, '') for c in word)

def collapse_doubles(ipa):
    c = r"[btdθdʒħxðɾzsʃsˤdˤtˤðˤʕɣfgklmnhwj]"
    return re.sub(rf"({c})\1", r"\1ə\1", ipa)

def tokenise(text):
    return re.findall(r'\w+|[^\w\s]', text, re.UNICODE)

def detect_sun(ipa, pos):
    for cl in SUN_ONSETS:
        if ipa[pos:].startswith(cl):
            return cl, len(cl)
    return None, 0

def apply_rules(ipa, word, prev=None, nxt=None):

    if word.endswith('ة'):
        end = (nxt in {',','،','.','!','?'} or nxt is None)
        if end:
            ipa = re.sub(r't$', 'ə', ipa)
        elif nxt and isinstance(nxt, str) and nxt.startswith('ال'):
            ipa = re.sub(r't$', 't', ipa)
        else:
            ipa = re.sub(r't$', 'ə', ipa)

    if 'w' in ipa or word.endswith('و') or word.endswith('وا'):
        if word == 'و':
            ipa = 'w'
        elif word.endswith('وا'):
            stem = word[:-2]
            ipa = map_chars(stem) + 'ʊ'
        elif ipa.endswith('w'):
            ipa = ipa[:-1] + 'ʊ'
        elif 'w' in ipa[1:]:
            ipa = ipa.replace('w', 'u:')
        elif ipa.startswith('w'):
            ipa = 'w' + ipa[1:]

    if 'j' in ipa or word.endswith('ي') or word == 'ي':
        if word == 'ي':
            ipa = 'jə'
        elif word.endswith('ي'):
            stem = word[:-1]
            ipa = map_chars(stem) + 'ɪ'
        else:
            ipa = ipa.replace('j', 'i:')

    if ipa.startswith('aː'):
        ipa = 'ə' + ipa[2:]
    elif ipa.startswith('ʔə'):
        ipa = 'ə' + ipa[2:]

    if ipa.startswith('aːl'):
        ipa = 'əl' + ipa[3:]
    elif ipa.startswith('waːl'):
        ipa = 'wəl' + ipa[4:]
    elif ipa.startswith('jaːl'):
        ipa = 'jəl' + ipa[4:]
    elif ipa.startswith('fiːl'):
        ipa = 'fɪl' + ipa[4:]
    elif ipa.startswith('fiː'):
        ipa = 'fɪl' + ipa[3:]
    elif ipa.startswith('biːl'):
        ipa = 'bɪl' + ipa[4:]
    elif ipa.startswith('biː'):
        ipa = 'bɪl' + ipa[3:]

    prefixes = ['əl','wəl','jəl','fɪl','bɪl']
    for p in prefixes:
        if ipa.startswith(p) and len(ipa) > len(p):
            onset, L = detect_sun(ipa, len(p))
            if onset:
                if p == 'əl':
                    head = 'ə'
                elif p == 'wəl':
                    head = 'wə'
                elif p == 'jəl':
                    head = 'jə'
                elif p == 'fɪl':
                    head = 'fɪ'
                else:
                    head = 'bɪ'
                rest = ipa[len(p)+L:]
                ipa = head + onset + 'ː' + rest
                break

    if prev and re.search(r'(?:a|e|i|o|u|ə|ʊ|ɪ|aː|iː|uː)$', prev):
        if ipa.startswith('əl'):
            ipa = 'l' + ipa[2:]
        elif ipa.startswith('wə'):
            ipa = 'w' + ipa[2:]
        elif ipa.startswith('jə'):
            ipa = 'j' + ipa[2:]
        elif ipa.startswith('ə'):
            ipa = ipa[1:]

    if prev and re.search(r'[aeiouəʊɪ]$', prev) and re.match(r'^[aeiouəʊɪ]', ipa):
        ipa = 'ʔ' + ipa

    return collapse_doubles(ipa)

def transcribe_fallback(word, prev=None, nxt=None):
    return apply_rules(map_chars(word), word, prev, nxt)

class HijaziTranscriber:
    def __init__(self, lexicon_path):
        self.lexicon = self.load_lexicon(lexicon_path)

    def load_lexicon(self, path):
        out = {}
        if not os.path.exists(path):
            return out
        with open(path, encoding='utf-8') as f:
            r = csv.reader(f)
            next(r, None)
            for row in r:
                if len(row) >= 2:
                    out[row[0].strip()] = row[1].strip()
        return out

    def transliterate(self, text, show_fallback=False):
        units = []
        for m in re.finditer(r'\s+|[^\s]+', text):
            seg = m.group()
            if seg.isspace():
                units.append(('space', seg))
            else:
                for t in tokenise(seg):
                    units.append(('token', t))

        out = []
        prev_ipa = None

        for i, (kind, val) in enumerate(units):
            if kind == 'space':
                out.append(val)
                continue

            nxt = None
            for j in range(i+1, len(units)):
                if units[j][0] == 'token':
                    nxt = units[j][1]
                    break

            clean = remove_diacritics(val)

            if clean in self.lexicon:
                ipa = apply_rules(self.lexicon[clean], clean, prev_ipa, nxt)
            else:
                ipa = transcribe_fallback(clean, prev_ipa, nxt)
                if show_fallback and re.match(r'^\w+$', val):
                    ipa += ' [F]'

            if prev_ipa and prev_ipa.endswith('n') and ipa.startswith('l'):
                prev_ipa = prev_ipa[:-1]
                ipa = 'lː' + ipa[1:]
                for k in range(len(out)-1, -1, -1):
                    if not out[k].isspace():
                        out[k] = prev_ipa
                        break

            out.append(ipa)
            prev_ipa = ipa

        return ''.join(out)

def launch_gui():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lexicon_path = os.path.join(script_dir, 'lexicon.csv')
    transcriber = HijaziTranscriber(lexicon_path)

    def on_go():
        text = input_box.get("1.0", tk.END)
        show = fallback_var.get()
        ipa = transcriber.transliterate(text, show)
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, ipa)

    root = tk.Tk()
    root.title("Hijazi IPA Pad")

    tk.Label(root, text="Arabic Input").pack()
    input_box = tk.Text(root, height=4, width=50)
    input_box.pack()

    fallback_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Show fallback tags", variable=fallback_var).pack()

    tk.Button(root, text="Transcribe", command=on_go).pack()

    tk.Label(root, text="IPA Output").pack()
    output_box = tk.Text(root, height=4, width=50)
    output_box.pack()

    root.mainloop()

if __name__ == "__main__":
    launch_gui()