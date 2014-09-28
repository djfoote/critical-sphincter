import xml.etree.ElementTree as etree
import random
import os
import argparse
import pickle

def write_essay(length):
    sentences = [ generate_sentence() for _ in range(length) ]
    sentences = map(str.capitalize, sentences)
    return str.join('. ', sentences) + '.\n'

def generate_sentence():
    words = [random.choice(list(bigrams.keys()))]

    next_word = next_from_b(words[-1])
    if not next_word:
        return str.join(' ', words)
    else:
        words.append(next_word)

    next_word = next_from_t(words)
    if not next_word:
        return str.join(' ', words)
    else:
        words.append(next_word)

    while True:
        next_word = next_from_q(words[-3:], len(words))
        if not next_word:
            break
        words.append(next_word)

    return str.join(' ', words)

# next_from_b :: word -> word
def next_from_b(prev):
    if prev in bigrams:
        return random.choice(bigrams[prev])
    return None

# next_from_t :: [word, word] -> word
def next_from_t(prev):
    prev_tup = tuple(prev)
    if prev_tup in trigrams:
        return random.choice(trigrams[prev_tup])
    return next_from_b(prev[1])

# next_from_q :: [word, word, word] -> word
def next_from_q(prev, word_count):
    prev_tup = tuple(prev)
    if prev_tup in quadgrams:
        if word_count > 10:
            for ender in enders:
                if ender in quadgrams[prev_tup]:
                    return ender
        return random.choice(quadgrams[prev_tup])
    return next_from_t(prev[1:])

def generate_sentence_enders():
    return [ w 
        for w in flatten(list(bigrams.values())) if w not in bigrams.keys() ]

def flatten(list_of_lists):
    result = []
    for lst in list_of_lists:
        result.extend(lst)
    return result

def refresh_dictionaries():
    def get_all(ngram):
        directory = ngram + 's'
        ngrams_list = []
        for f in os.listdir(os.getcwd() + '/' + directory):
            tree = etree.parse(directory + '/' + f)
            root = tree.getroot()
            all_ngrams = root.findall(ngram)
            ngrams_list.extend([ g for g in all_ngrams if '#' not in g.text ])
        return ngrams_list

    for b in get_all('bigram'):
        words = b.text.split()
        if words[0] in bigrams:
            bigrams[words[0]].append(words[1])
        else:
            bigrams[words[0]] = [words[1]]

    for t in get_all('trigram'):
        words = t.text.split()
        if (words[0], words[1]) in trigrams:
            trigrams[(words[0], words[1])].append(words[2])
        else:
            trigrams[(words[0], words[1])] = [words[2]]

    for q in get_all('quadgram'):
        words = q.text.split()
        if (words[0], words[1], words[2]) in quadgrams:
            quadgrams[(words[0], words[1], words[2])].append(words[3])
        else:
            quadgrams[(words[0], words[1], words[2])] = [words[3]]

    enders.extend(generate_sentence_enders())
    pickle_dictionaries()

def unpickle_dictionaries():
    with open('bigram_dict', 'rb') as infile:
        bigrams.update(pickle.load(infile))
    with open('trigram_dict', 'rb') as infile:
        trigrams.update(pickle.load(infile))
    with open('quadgram_dict', 'rb') as infile:
        quadgrams.update(pickle.load(infile))
    with open('enders_list', 'rb') as infile:
        enders.extend(pickle.load(infile))

def pickle_dictionaries():
    with open('bigram_dict', 'wb') as outfile:
        pickle.dump(bigrams, outfile)
    with open('trigram_dict', 'wb') as outfile:
        pickle.dump(trigrams, outfile)
    with open('quadgram_dict ', 'wb') as outfile:
        pickle.dump(quadgrams, outfile)
    with open('enders_list', 'wb') as outfile:
        pickle.dump(enders, outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generates bullshit for all your rhetorical essay needs.')
    parser.add_argument('-r', '--refresh-dictionaries', default=False,
        action='store_true', help='Update data for sentence generation.')
    args = parser.parse_args()
    
    bigrams   = {} #  word              -> [word]
    trigrams  = {} # (word, word)       -> [word]
    quadgrams = {} # (word, word, word) -> [word]
    enders    = [] # words that end sentences

    if args.refresh_dictionaries:
        refresh_dictionaries()
    else:
        unpickle_dictionaries()
