from transformers import BertForSequenceClassification, BertConfig
import torch
from transformers import BertModel
import pickle
from transformers import BertTokenizer
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
import re
import pandas as pd
from newspaper import Article
import torch.nn.functional as F
import numpy as np
from bs4 import BeautifulSoup as bs
import json
import requests
from newspaper import Config
from newspaper.utils import BeautifulSoup
from BertClass import BertClassifier
import os
from newsapi import NewsApiClient

MAX_LEN=512
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
device = torch.device("cuda")

def config(path='bert.pickle'):
    with open(path, 'rb') as fp:
        bert_model = pickle.load(fp)
    return bert_model


def text_preprocessing(text):
    text = re.sub(r'(@.*?)[\s]', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def preprocessing_for_bert(data):
    """Text pre-processing for BERT model
    """
    input_ids = []
    attention_masks = []

    for sent in data:
        encoded_sent = tokenizer.encode_plus(
            text=text_preprocessing(sent),  # Preprocess sentence
            add_special_tokens=True,  # Add `[CLS]` and `[SEP]`
            max_length=MAX_LEN,  # Max length to truncate/pad
            pad_to_max_length=True,  # Pad sentence to max length
            # return_tensors='pt',           # Return PyTorch tensor
            return_attention_mask=True,
            truncation=True  # Return attention mask
        )

        input_ids.append(encoded_sent.get('input_ids'))
        attention_masks.append(encoded_sent.get('attention_mask'))

    input_ids = torch.tensor(input_ids)
    attention_masks = torch.tensor(attention_masks)
    return input_ids, attention_masks


def bert_predict(model, test_dataloader):
    """Perform a forward pass on the trained BERT model to predict probabilities
    on the test set.
    """

    model.eval()
    all_logits = []
    for batch in test_dataloader:
        b_input_ids, b_attn_mask = tuple(t.to(device) for t in batch)[:2]
        with torch.no_grad():
            logits = model(b_input_ids, b_attn_mask)
        all_logits.append(logits)
    all_logits = torch.cat(all_logits, dim=0)
    probs = F.softmax(all_logits, dim=1).cpu().numpy()
    return probs

def parse_url(url):
    """Parse the url to obtain texts,title and image
    """
    news = Article(url)
    news.download()
    news.parse()
    if url.startswith('https://www.bbc.com'):
        article = requests.get(url)
        soup = bs(article.content, "html.parser")
        text = ''
        for EachPart in soup.select('div[class*="RichTextContainer"]'):
            for p in EachPart.find_all("p"):
                text = text + ' ' + p.text
    else:
        news = Article(url)
        news.download()
        news.parse()
        text = news.text
    title = news.title
    image = news.top_image
    return text,title,image

def predicttext(text,bert_model=None):
  data=[]
  data.append(text)
  a= np.array(data)
  data_to_test = pd.Series(a)
  test_inputs, test_masks = preprocessing_for_bert(data_to_test)
  test_dataset = TensorDataset(test_inputs, test_masks)
  test_sampler = SequentialSampler(test_dataset)
  test_dataloader = DataLoader(test_dataset, sampler=test_sampler, batch_size=2)
  prob = bert_predict(bert_model, test_dataloader)
  return prob[0,1]

def web_predict(url,bert_model = None):
    if bert_model == None:
        bert_model = config()
    text,title,image=parse_url(url)
    text = title+text
    a = 0.9
    b = 1 - a
    textlist = text.split(" ")
    if len(textlist) <= 510:
        text = " ".join(textlist)
        prob = predicttext(text)
    elif len(textlist) > 510:
        textlist1 = textlist[0:510]
        textlist2 = textlist[510:]
        text1 = " ".join(textlist1)
        text2 = " ".join(textlist2)
        score1 = predicttext(text1)
        score2 = predicttext(text2)
        prob = a * score1 + b * score2
    return prob

def get_daily_news():
    apikey = 'd864bc32cb2b417db3008afa3d94b354'
    url = []
    api = NewsApiClient(api_key=apikey)
    data = api.get_top_headlines(sources = 'fox-news', language ='en')
    length = len(data['articles'])
    for num in range(0, length):
        url.append(data['articles'][num]['url'])
        print(data['articles'][num]['url'])
