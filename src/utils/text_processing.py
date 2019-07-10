from urlextract import URLExtract


def extract_urls(text):
    return URLExtract().find_urls(text)
