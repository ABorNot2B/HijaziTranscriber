## Features
- Lexicon-based IPA transcription for Hijazi Arabic
- Diacritic stripping for input normalization
- ~~[UNK] tagging for out-of-vocabulary words~~ v1.1 is supports fallback, see details below
- UTF-8 safe
- GUI mode

## Limitations
- Only one IPA variant per word is retained. Future versions may support variant-aware transcription.
- ~~Lexicon must be manually curated. [UNK] is returned for missing entries.~~ v1.1 is supports fallback, see details below.

## v1.1 Release Notes: 
HijaziTranscriber now includes a custom fallback transcriber for [UNK] words fr. When a word is not found in the lexicon, the tool applies a 1:1 character-to-IPA mapping with phonological rules tailored to Hijazi Arabic. A GUI toggle lets users choose whether to display fallback tags ([F]) for transparency.

# What’s New
- Fallback-aware transcription with rule-based IPA
- [F] tags for out-of-lexicon words
- GUI checkbox to toggle fallback visibility

# dialect-sensitive custom transcriber + phonological rules are as follows:
<pre>
ا,aː
ب,b
ت,t
ث,t
ج,d͡ʒ
ح,ħ
خ,x
د,d
ذ,d
ر,ɾ
ز,z
س,s
ش,ʃ
ص,sˤ
ض,dˤ
ط,tˤ
ظ,ðˤ
ع,ʕ
غ,ɣ
ف,f
ق,g
ك,k
ل,l
م,m
ن,n
ه,h
و,uː
ي,iː
ى,ə
ء,ʔ
أ,ʔ
إ,ʔɪ
ؤ,ʔʊ
ئ,ʔə
‎ ّ,ː

.Phonological Rules Included
- ة → ə if final, t elsewhere
- w: → w if word initial
- a:l → əl
- Sun letter assimilation: əlX → əX: (X = sun consonant)
- u: → w if  word-initial or standalone
- i: → je if word-initial or standalone

</pre>

This update reflects a shift from dependency to autonomy. Ongoing work includes expanding the lexicon and refining rule coverage to better capture Hijazi-specific patterns.


## Citation
If you use this tool in academic work, please cite: Alharthi (2025). HijaziTranscriber: A Lexicon-Based IPA Tool for Hijazi Arabic. GitHub. https://github.com/ABorNot2B/HijaziTranscriber

## License
This project is licensed under CC BY-NC-SA 4.0.
(please see license file in this repo)
