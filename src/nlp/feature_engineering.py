import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from src.nlp.lexicon import SentimentLexiconFeaturizer

class UnifiedFeatureExtractor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UnifiedFeatureExtractor, cls).__new__(cls)
            cls._instance._init_model()
        return cls._instance

    def _init_model(self):
        model_path = "/home/muhammad/.cache/huggingface/hub/models--HooshvareLab--bert-fa-base-uncased-sentiment-digikala/snapshots/88db8245349b36b47ef1b92e49b8b80428b77d7c"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModel.from_pretrained(model_path)
        self.lexicon = SentimentLexiconFeaturizer()
        self.model.eval()

    def get_features(self, sentences):
        if isinstance(sentences, str):
            sentences = [sentences]
            
        batch_size = 4
        all_embeddings = []
        
        for i in range(0, len(sentences), batch_size):
            batch = sentences[i:i + batch_size]
            inputs = self.tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=128)
            with torch.no_grad():
                outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :].numpy()
            all_embeddings.append(embeddings)
            
        bert_features = np.vstack(all_embeddings)
        
        # اصلاح: تبدیل خروجی لکسیکون به آرایه عددی (حتی اگر دیکشنری باشد)
        lex_list = []
        for s in sentences:
            feat = self.lexicon.get_features(s)
            if isinstance(feat, dict):
                lex_list.append(list(feat.values()))
            else:
                lex_list.append(feat)
                
        lexicon_features = np.array(lex_list, dtype=float)
        
        return np.hstack([bert_features, lexicon_features])
