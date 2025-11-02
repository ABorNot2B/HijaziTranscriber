import csv
import re
import tkinter as tk

def remove_diacritics(text):
    diacritics = re.compile(r'[\u064B-\u0652\u0670\u06D6-\u06ED]')
    return diacritics.sub('', text)

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

    def transliterate(self, utterance):
        words = utterance.strip().split()
        ipa_sequence = []
        for word in words:
            clean_word = remove_diacritics(word)
            ipa = self.lexicon.get(clean_word, '[UNK]')
            ipa_sequence.append(ipa)
        return ' '.join(ipa_sequence)

def launch_gui():
    transcriber = HijaziTranscriber('lexicon.csv')

    def on_transcribe():
        input_text = input_box.get("1.0", tk.END).strip()
        ipa = transcriber.transliterate(input_text)
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, ipa)

    root = tk.Tk()
    root.title("Hijazi IPA Pad")

    tk.Label(root, text="Arabic Input").pack()
    input_box = tk.Text(root, height=4, width=50)
    input_box.pack()

    tk.Button(root, text="Transcribe", command=on_transcribe).pack()

    tk.Label(root, text="IPA Output").pack()
    output_box = tk.Text(root, height=4, width=50)
    output_box.pack()

    root.mainloop()

if __name__ == "__main__":
    launch_gui()