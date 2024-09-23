import pandas as pd
import re
import logging
from nltk.stem import PorterStemmer
from spellchecker import SpellChecker
from flask import Flask, request, render_template, jsonify

# Initialize the flask App
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)


def fetch_data_from_csv(file_path):
    df = pd.read_csv(file_path)
    text_data = " ".join(df['text'].dropna().tolist())
    return text_data


def index_words(text):
    index = {}
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    for sentence_idx, sentence in enumerate(sentences):
        words = re.findall(r'\w+', sentence)
        for position, word in enumerate(words):
            word = word.lower()
            if word in index:
                index[word]['count'] += 1
                index[word]['positions'].append((sentence_idx, position))
            else:
                index[word] = {'count': 1, 'positions': [(sentence_idx, position)]}
    return index, sentences


def remove_stop_words(index):
    stop_words = {'a', 'an', 'the', 'and', 'or', 'in', 'on', 'at'}
    for stop_word in stop_words:
        if stop_word in index:
            del index[stop_word]
    return index


def apply_stemming(index):
    stemmer = PorterStemmer()
    stemmed_index = {}
    for word, data in index.items():
        stemmed_word = stemmer.stem(word)
        if stemmed_word in stemmed_index:
            stemmed_index[stemmed_word]['count'] += data['count']
            stemmed_index[stemmed_word]['positions'].extend(data['positions'])
        else:
            stemmed_index[stemmed_word] = {'count': data['count'], 'positions': data['positions']}
    return stemmed_index


def correct_spelling(query, vocabulary):
    spell = SpellChecker()
    spell.word_frequency.load_words(vocabulary)
    words = query.split()
    corrected_words = [spell.correction(word) for word in words]
    corrected_query = ' '.join(corrected_words)
    return corrected_query


def get_autocomplete_suggestions(query, vocabulary, num_suggestions=5):
    suggestions = [word for word in vocabulary if word.startswith(query)]
    return suggestions[:num_suggestions]


def search(query, index, sentences):
    query_words = re.findall(r'\w+', query.lower())
    results = {}
    for word in query_words:
        if word in index:
            results[word] = {
                'count': index[word]['count'],
                'positions': index[word]['positions'],
                'sentences': [sentences[idx] for idx, _ in index[word]['positions']]
            }
    return results


def search_engine(file_path, query):
    text_data = fetch_data_from_csv(file_path)
    index, sentences = index_words(text_data)
    index = remove_stop_words(index)
    index = apply_stemming(index)

    vocabulary = list(index.keys())
    corrected_query = correct_spelling(query, vocabulary)
    suggestions = get_autocomplete_suggestions(corrected_query, vocabulary)
    results = search(corrected_query, index, sentences)
    return results, suggestions


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search_query():
    query = request.form['query']
    file_path = 'health_data.csv'  # Replace with the path to your CSV file
    results, suggestions = search_engine(file_path, query)
    return render_template('results.html', query=query, results=results, suggestions=suggestions)


@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    query = request.form.get('query', '')
    file_path = 'health_data.csv'

    # Fetch and process fresh data
    text_data = fetch_data_from_csv(file_path)
    index, _ = index_words(text_data)
    index = remove_stop_words(index)
    index = apply_stemming(index)

    vocabulary = list(index.keys())
    corrected_query = correct_spelling(query, vocabulary)
    suggestions = get_autocomplete_suggestions(corrected_query, vocabulary)

    response = jsonify({
        'suggestions': suggestions,
        'corrected_query': corrected_query
    })
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    logging.debug(f"Query: {query}")
    logging.debug(f"Vocabulary: {vocabulary}")
    logging.debug(f"Corrected Query: {corrected_query}")
    logging.debug(f"Suggestions: {suggestions}")

    return response


if __name__ == '__main__':
    app.run(debug=True)



























