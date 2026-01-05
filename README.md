## HijaziTranscriber: Version 2.4 Overview
This tool was developed as part of my Hijazi Arabic Corpus project.
To support transparency and reproducibility, the full corpus is publicly accessible:
Google Drive:
https://drive.google.com/drive/folders/1f_oIOTuoxnJ394sLFAPFKHRLbKDmDZmJ

___
## Tool Features (v2.4)
- Lexicon‑based IPA transcription for Hijazi Arabic
- Rule‑based fallback transcriber for out‑of‑lexicon words
- Full phonological pipeline (Hijazi‑specific)
- Diacritic stripping
- UTF‑8 safe
- GUI mode
- Exact preservation of input spacing and punctuation
- Safe lexicon loading (tool runs even if lexicon.csv is missing, defaults to rule-based fallback)
- Updated portability (lexicon.csv does not need to be on desktop to load up)

___
## Limitations
- Only one IPA variant per word is retained. Future versions may support variant-aware transcription.
- Fallback system transcribes 1:1 (Arabic grapheme to IPA symbol).

___
## Version History:

## v1.1 Notes: 
HijaziTranscriber now includes a custom fallback transcriber for [UNK] words. When a word is not found in the lexicon, the tool applies a 1:1 character-to-IPA mapping with phonological rules tailored to Hijazi Arabic. A GUI toggle lets users choose whether to display fallback tags ([F]) for transparency.

**What’s New (v1.1)**
- Fallback-aware transcription with rule-based IPA
- [F] tags for out-of-lexicon words
- GUI checkbox to toggle fallback visibility

**dialect-sensitive custom transcriber + phonological rules are as follows:**
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
</pre>

**Phonological Rules Included:**
<pre>
- ة → ə if final, t elsewhere
- w: → w if word initial
- a:l → əl
- Sun letter assimilation: əlX → əX: (X = sun consonant)
- u: → w if  word-initial or standalone
- i: → je if word-initial or standalone
</pre>
**all these rules have been updated in newer versions**

___
  ## v2.1 NOTES:
  
This version includes a number of phonological rules implemented into the tool's logic to refine its accuracy. These rules are as follows:

**Phonological Rules:**


**Taa Marbuta (ة):**

-Surfaces as [ə] if sentence‑final or before punctuation (comma, period, etc.).

-Surfaces as [t] only if immediately followed by a definite article (ال).

-Otherwise defaults to [ə].


  
**Waw (و):**

**note: this rule has been updated in v2.4**

-[w] if stand‑alone or word‑initial.

-[uː] if mid‑word or word‑final.


  
**Ya' (ي):**

**note: this rule has been updated in v2.4**

-[jə] if stand‑alone.

-[j] if word‑initial.

-[iː] if mid‑word or word‑final.

___
## v2.2 Notes:
**Definite Article (ال)**
Version 2.1 exhibited a few limitations when handling the Arabic definite article ال.
This necessitated a patch including a multi-step approach to handling this prefix and others as shown below:

**STEP 1:**

Prefix ∈ {Ø, w, j, fɪ, bɪ}
Vowel = ə for Ø/w/j, ɪ for fɪ/bɪ (ɪ replaces schwa)
Form = PREFIX + l + ROOT
Examples: البيت → əlbe:t, في البيت → fɪlbe:t, بالطريق → bɪtˤːariːg


**STEP 2:**

Sun‑letter assimilation → (PREFIX + ə/ɪ) + l + SUN → PREFIX + ə/ɪ + SUNː
Examples: الشمس → əʃːams, والشمس → wəʃːams, في الشمس → fɪʃːams


**STEP 3:** 

Sandhi → after vowel‑final words, drop schwa for Ø/w/j; retain ɪ for fɪ/bɪ.
Examples: في البيت → filbe:t, هو بالبيت → hu bɪlbe:t


**Cross‑Word Assimilation:**


-n + l → lː (final n deleted, following l lengthened).

  
**Double Consonant Collapse:**
**note: this rule has been updated in v2.4**


-Identical consonants in succession collapse to a single consonant (as Arabic phonotactics do not allow the same consonant sound twice without gemination).

___
**Technical Improvements (v2.2):**

-No [UNK] tokens: unmapped characters drop silently instead of surfacing as [UNK].

-Safe lexicon loading: GUI launches even if lexicon.csv is missing or malformed.

-Tkinter GUI stability: ensured clean startup with root.mainloop() and error‑safe fallbacks.

-Regex assimilation logic: unified handling of əl, waːl, and jaːl prefixes for sun letters.

___
## v2.3 Notes:
Lexicon expansion from 2,322 unique word types to 2,799 (from 5,219 lexical items to 6,377 overall).

___
## v2.4 Notes: 
This version included **updated portability** of the tool. It can now load up lexicon.csv from the same file to which HT is downloaded.
This version also included some reworkings of previous rules:
<pre>

**1. و (Waw)**
- w if standalone
- w if word‑initial
- u: if mid‑word
- ʊ if word‑final
- ʊ if final وا


**2. ي (Ya’)**
- jə if standalone
- ɪ if word‑final
- i: if mid‑word
- i: if word‑initial (no more [j] initial)

  
**3. Initial Alif Normalization**
Only the following reduce to schwa:
- ا (aː → ə)
- أ (ʔə → ə)
**4. Double Consonant Handling (NEW in v2.4)**
If two identical consonants appear adjacent in IPA:
CC → CəC
  
</pre>
___
## Citation
If you use this tool in academic work, please cite: Alharthi (2025). HijaziTranscriber: A Lexicon-Based IPA Tool for Hijazi Arabic. GitHub. https://github.com/ABorNot2B/HijaziTranscriber

___
## License
This project is licensed under CC BY-NC-SA 4.0.
(please see license file in this repo)
