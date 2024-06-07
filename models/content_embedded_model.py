from typing import Union
from pydantic import BaseModel
from datetime import datetime
from fastapi import HTTPException
import re, os, json, requests
from bs4 import BeautifulSoup

class ContentEmbeddedModel(BaseModel):
    data_id: int
    data_type: str
    name: str = ''
    description: str = ''
    content: Union[str, None] = None
    counter: int = 0
    modify_date: Union[datetime, None] = None
    active: bool
    info_exist: bool

    def __init__(self, **data):
        super().__init__(**data)
        
        if self.content is not None and isinstance(self.content, str):
            self.content = self.content.strip()
            self.content = self.clean_html(self.content)
        elif self.content is not None and not isinstance(self.content, str):
            raise HTTPException(status_code=404, detail="content must be a string.")
        
        if not self.modify_date:
            self.modify_date = datetime.now()

    def clean_html(self, html, word_sep='|||'):
        soup = BeautifulSoup(html, 'lxml')
        separate_text = soup.get_text(strip=True, separator=word_sep).split(word_sep)
        new_text = []
        for text in separate_text:
            clean_text = re.sub(r'\s+', ' ', text).strip()
            if clean_text:
                new_text.append(clean_text)
        if len(new_text) > 2:
            return new_text
        else:
            return None

    def get_content(self):
        if isinstance(self.content, list):
            return ' '.join(self.content)
        else:
            return self.content

    def count_tokens(self):
        url_tokenizer = os.getenv("TOKENIZER_COUNTER_API_URL", "")
        headers_sentence = {"Content-Type": "application/json", "Authorization": "Bearer " + os.getenv("TOKENIZER_COUNTER_API_TOKEN")}
        payload_sentence = json.dumps({"sentences": self.content})
        response_sentence = requests.request("POST", url_tokenizer, headers=headers_sentence, data=payload_sentence)
        tokens = response_sentence.json()
        return tokens['token_count']

    def split_content_token(self, max_tokens=512):
        tokenized_text = self.count_tokens()
        text_elements = []
        current_text = ''
        current_tokens = 0
        for text, tokens in zip(self.content, tokenized_text):
            if text:
                if current_tokens + tokens > max_tokens:
                    text_elements.append(current_text)
                    current_text = text
                    current_tokens = tokens
                else:
                    current_text = " ".join([current_text, text]) if current_text else text
                    current_tokens += tokens
        if current_text:
            text_elements.append(current_text)
        self.content = self.get_content()
        return text_elements

    class Config:
        json_schema_extra = {
            "example": {
                "data_id": 0,
                "data_type": "product",
                "name": "product name",
                "content": "product content",
                "counter": 0,
                "modify_date": "2021-10-01 00:00:00",
                "active": True,
                "info_exist": True
            }
        }
