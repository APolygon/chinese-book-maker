from wordfreq import word_frequency

# Your list of entries (pinyin, traditional, meaning)
entries = [
    ("lóng", "龍", "Drache"),
    ("zhǎng", "長", "lang"),
    ("zhōng", "中", "Mitte"),
    ("guó", "國", "Land"),
    ("rén", "人", "Person"),
    ("yī", "一", "eins"),
    ("yīng wǔ", "鸚鵡", "Papagei"),
    ("shā fā", "沙發", "Sofa"),
    ("xǐ wǎn chí", "洗碗池", "Spülbecken / Spüle"),
    ("mǎ tǒng", "馬桶", "Toilette")
]

# Add frequency scores (using 'zh' for Mandarin Chinese with best wordlist)
entries_with_freq = [
    (pinyin, hanzi, meaning, word_frequency(hanzi, 'zh', wordlist='best'))
    for pinyin, hanzi, meaning in entries
]

# Sort by frequency in descending order
sorted_entries = sorted(entries_with_freq, key=lambda x: x[3], reverse=True)

# Print results
for pinyin, hanzi, meaning, freq in sorted_entries:
    print(f"{hanzi} ({pinyin}): {meaning} — freq: {freq:.6f}")