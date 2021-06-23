from underthesea import sent_tokenize


def break_passages(content, min_words: int = 80, max_words: int = 120):
    sentences = sent_tokenize(content)
    passages = []
    passage = []
    for sent in sentences:
        words = sent.split()
        if len(passage) + len(words) <= max_words:
            passage.extend(words)
        if len(passage) >= min_words:
            passages.append(" ".join(passage))
            passage = []

    if len(passage) < min_words:
        try:
            if len(passage) + len(passages[-1].split()) < max_words:
                passages[-1] = passages[-1] + " ".join(passage)
            else:
                passages.append(" ".join(passage))
        except IndexError as e: # when len(passages) = 0
            passages.append(" ".join(passage))

    return passages