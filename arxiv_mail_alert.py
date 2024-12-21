import yaml
import urllib.request
import feedparser
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import argparse

def arxiv_alert(categories=None, keywords=None, authors=None, max_results=10):
    base_url = 'http://export.arxiv.org/api/query?'

    # Build the query string
    search_query = str()

    if categories:
        search_query += '%28' + '+OR+'.join(f'cat:{cat}' for cat in categories) + '%29'

    if keywords:
        if search_query:
            search_query += '+AND+%28'
        else:
            search_query += '%28'
        search_query += '+OR+'.join(f'ti:%22{kw}%22' for kw in keywords)
        search_query += '+OR+' + '+OR+'.join(f'abs:%22{kw}%22' for kw in keywords) + '%29'

    if authors:
        if search_query:
            search_query += '+AND+%28'
        else:
            search_query += '%28'
        search_query += '+OR+'.join(f'au:%22{author}%22' for author in authors) + '%29'

    # Add sorting and limits
    query = f'search_query={search_query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending'
    url = base_url + query

    # Fetch and parse data
    response = urllib.request.urlopen(url).read()
    feed = feedparser.parse(response)

    # Prepare HTML content
    body = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
        h1 { color: #333; }
        .entry { margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background: #f9f9f9; }
        .entry h2 { margin: 0; font-size: 18px; color: #007BFF; }
        .entry p { margin: 5px 0; }
    </style>
    </head>
    <body>
    <h1>ArXiv Alert</h1>
    <p>Latest papers on your topics of interest:</p>
    """

    for entry in feed.entries:
        published_date = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ')

        # Safely access attributes
        title = getattr(entry, 'title', 'No Title Available')
        summary = getattr(entry, 'summary', 'No Summary Available')
        pdf_link = next((link.href for link in entry.links if getattr(link, 'title', '') == 'pdf'), '#')
        authors = ', '.join(getattr(author, 'name', 'Unknown Author') for author in entry.authors)
        categories = ', '.join(tag.get('term', 'Unknown Category') for tag in getattr(entry, 'tags', []))

        body += f"""
        <div class="entry">
            <a href="{pdf_link}"><h2>{title}</h2></a>
            <p><strong>Published:</strong> {published_date.strftime('%d %b %Y')}</p>
            <p><strong>Authors:</strong> {authors}</p>
            <p><strong>Categories:</strong> {categories}</p>
            <p><strong>Abstract:</strong> {summary}</p>
        </div>
        """

    body += "</body></html>"
    return body

def load_config(args):
    with open(args.config_path, 'r') as f:
        try:
            config_dict = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(exc)
            return None
    return config_dict

def process_config(config_dict):
    categories = config_dict.get('categories', [])
    keywords = config_dict.get('keywords', [])
    authors = config_dict.get('authors', [])
    max_results = config_dict.get('max_results', 10)

    def format_phrase(phrases):
        """Format phrases to be used in the query"""
        formatted_phrases = []
        for phrase in phrases:
            phrase = phrase.strip()
            if " " in phrase:
                phrase = "%22" + phrase.replace(" ", "+") + "%22"
            formatted_phrases.append(phrase)
        return formatted_phrases

    keywords = format_phrase(keywords)
    authors = format_phrase(authors)
    return categories, keywords, authors, max_results

def send_email(body, config_dict):
    now = datetime.now()
    subject = f"ArXiv Alert - {now.strftime('%d %b %Y')}"
    sender = config_dict['sender']
    password = config_dict['sender_password']
    receivers = config_dict['receivers']

    # Create email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(receivers)

    # Add plain text and HTML versions
    plain_text = "Your daily ArXiv alert. Open in an email client that supports HTML to see full content."
    msg.attach(MIMEText(plain_text, 'plain'))
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP_SSL(config_dict['smtp_host'], config_dict['smtp_port']) as server:
            server.login(sender, password)
            server.sendmail(sender, receivers, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_path', type=str, default='config-demo.yaml', help='Path to the YAML configuration file')
    args = parser.parse_args()

    # Load and process configuration
    config_dict = load_config(args)
    if not config_dict:
        exit(1)

    categories, keywords, authors, max_results = process_config(config_dict)
    mail_body = arxiv_alert(categories, keywords, authors, max_results)

    # Send email
    send_email(mail_body, config_dict)
