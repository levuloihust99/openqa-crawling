import re
import string
import unicodedata
from typing import Dict, List, Tuple, Text, Optional
import sqlite3
from sqlite3 import Error

SQLITE_DB = "resources.db"


def remove_whitespaces(text):
    text = re.sub(r"\s+", r" ", text)
    return text


def remove_special_symbols(text):
    punctuation = re.escape(string.punctuation)
    vietnamese_accents = "àáãạảăắằẳẵặâấầẩẫậèéẹẻẽêềếểễệđìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳỵỷỹýÀÁÃẠẢĂẮẰẲẴẶÂẤẦẨẪẬÈÉẸẺẼÊỀẾỂỄỆĐÌÍĨỈỊÒÓÕỌỎÔỐỒỔỖỘƠỚỜỞỠỢÙÚŨỤỦƯỨỪỬỮỰỲỴỶỸÝ"
    alpha_numeric = "0-9a-zA-Z"
    regex_pattern = re.compile(r"[^{}{}{}\s]".format(alpha_numeric, vietnamese_accents, punctuation))
    return regex_pattern.sub("", text)


def remove_leading_non_alphanumeric(text):
    vietnamese_accents = "àáãạảăắằẳẵặâấầẩẫậèéẹẻẽêềếểễệđìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳỵỷỹýÀÁÃẠẢĂẮẰẲẴẶÂẤẦẨẪẬÈÉẸẺẼÊỀẾỂỄỆĐÌÍĨỈỊÒÓÕỌỎÔỐỒỔỖỘƠỚỜỞỠỢÙÚŨỤỦƯỨỪỬỮỰỲỴỶỸÝ"
    text = re.sub(r"^[^A-Za-z{}]+".format(vietnamese_accents), r"", text)
    return text


def remove_last_row(text):
    text = text.split("\n")

    try:
        while not text[-1]:
            text.pop()
        text.pop()
    except Exception as e:
        return ""

    return "\n".join(text)


def normalize(text):
    return unicodedata.normalize('NFC', text)