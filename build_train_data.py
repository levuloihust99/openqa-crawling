import mysql.connector
import json
from preprocess import normalize, remove_leading_non_alphanumeric, remove_special_symbols, remove_whitespaces
import re


def process_pipeline(text):
    text = normalize(text)
    text = remove_leading_non_alphanumeric(text)
    text = remove_special_symbols(text)
    text = remove_whitespaces(text)
    return text


def build_json():
    config = {
        'user': 'djangouser',
        'password': '9VINsmoke9',
        'database': 'qa_annotate',
        'host': '34.101.81.157',
        'raise_on_warnings': True,
        'auth_plugin': 'mysql_native_password'
    }

    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    JOIN_QUERY = "SELECT tag_qasample.id, positive_document, positive_document_title, question, hard_negative_document, hard_negative_document_title, answer FROM `tag_qasample` INNER JOIN `tag_answer` ON tag_qasample.id = tag_answer.sample_id;"
    
    cursor.execute(JOIN_QUERY)
    records = {}
    for id, positive_document, positive_document_title, question, hard_negative_document, hard_negative_document_title, answer in cursor:
        if not question or not hard_negative_document or not hard_negative_document_title:
            continue
        
        if positive_document.startswith("Suckhoedoisong.vn"):
            positive_document = positive_document[len("Suckhoedoisong.vn"):]
        if hard_negative_document.startswith("Suckhoedoisong.vn"):
            hard_negative_document = hard_negative_document[len("Suckhoedoisong.vn"):]
        
        positive_document = re.sub(r"\[SEP\]", "", positive_document)
        positive_document = process_pipeline(positive_document)
        positive_document_title = process_pipeline(positive_document_title)
        hard_negative_document = process_pipeline(hard_negative_document)
        hard_negative_document_title = process_pipeline(hard_negative_document_title)
        question = re.sub(r"\[SEP\]", "", question)
        question = process_pipeline(question)
        
        if id in records:
            records[id]['answers'].append(answer)
        else:
            records[id] = {
                'question': question,
                'answers': [answer],
                'positive_ctxs': [
                    {
                        'title': positive_document_title,
                        'text': positive_document
                    }
                ],
                'hard_negative_ctxs': [
                    {
                        'title': hard_negative_document_title,
                        'text': hard_negative_document
                    }
                ]
            }
        
    reform_records = [v for v in records.values()]
    with open("data/vicovid-train_V3.json", "w") as writer:
        json.dump(reform_records, writer, ensure_ascii=False, indent=4)

    
if __name__ == "__main__":
    build_json()