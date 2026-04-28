import nltk
import warnings
warnings.filterwarnings('ignore', message="urllib3 (.*) or chardet (.*) doesn\'t match a supported version!")

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

def summarize_url(url, language="english",sentence_count=10):
    """
    Summarizes the URL given in the desired language
    
    Args:
        url: The URL to be summarized
        language: The language for the URL to be summary to be in
        sentence_count: The number of sentences the summary should be

    Returns:
        summary: The summary of the url as a string
    """


    LANGUAGE = language
    SENTENCES_COUNT = sentence_count
    parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    # or for plain text files
    # parser = PlaintextParser.from_file("document.txt", Tokenizer(LANGUAGE))
    # parser = PlaintextParser.from_string("Check this out.", Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    summary = ""
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        summary += str(sentence) + "\n"
    return summary

def main():
    url = "https://www.snhu.edu/about-us/newsroom/education/student-stress"
    summary = summarize_url(url,sentence_count=10)
    print(summary)

nltk.download('punkt_tab', quiet=True)

if __name__ == "__main__":
    main()