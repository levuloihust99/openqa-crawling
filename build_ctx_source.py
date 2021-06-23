import mysql.connector
from preprocess import normalize, remove_last_row, remove_special_symbols, remove_whitespaces, remove_leading_non_alphanumeric
from utils import break_passages
import pandas as pd


if __name__ == "__main__":
    config = {
        'user': 'levuloi',
        'password': '9VINsmoke9',
        'database': 'resources',
        'host': 'localhost',
        'raise_on_warnings': True,
        'auth_plugin': 'mysql_native_password'
    }

    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SELECT_QUERY = r"""SELECT * FROM `medical_articles`;"""
    cursor.execute(SELECT_QUERY)
    records = []
    count = 0
    for id, url, title, summary, content in cursor:
        title = normalize(title)
        title = remove_leading_non_alphanumeric(title)
        title = remove_whitespaces(title)
        title = remove_special_symbols(title)

        summary = normalize(summary)
        if summary.startswith("Suckhoedoisong.vn"):
            summary = summary[len("Suckhoedoisong.vn"):]
        summary = remove_leading_non_alphanumeric(summary)
        summary = remove_whitespaces(summary)
        summary = remove_special_symbols(summary)

        content = normalize(content)
        content = remove_leading_non_alphanumeric(content)
        content = remove_last_row(content)
        content = remove_whitespaces(content)
        content = remove_special_symbols(content)

        passages = break_passages(content)
        passages = [summary] + passages

        records.extend([
            {
                'title': title,
                'text': text
            }
            for text in passages
        ])

        count += 1
        if count % 10 == 0:
            print("Done {} records".format(count))

    idxs = range(1, len(records) + 1)
    titles = []
    texts = []
    for record in records:
        titles.append(record['title'])
        texts.append(record['text'])
    
    df_dict = {
        'id': idxs,
        'text': texts,
        'title': titles
    }
    df = pd.DataFrame(df_dict)

    df.to_csv("data/vicovid_ctx_sources_V2.tsv", sep='\t', header=True, index=False)