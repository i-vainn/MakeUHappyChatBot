from transformers import GPT2Model, GPT2Tokenizer
from tqdm import tqdm_notebook
import numpy as np
import hnswlib as hnsw
import torch

class EmbeddingCreator:
    def __init__(self, model_name_or_path="sberbank-ai/rugpt3small_based_on_gpt2"):
        '''For usage examples go to ~/junk/run_this_all.ipynb'''

        self.words = None

        self.device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name_or_path)
        self.model = GPT2Model.from_pretrained(model_name_or_path).to(self.device)
        
    def tokenize(self, data):
        tokenized = [self.tokenizer.encode(x, return_tensors="pt").to(self.device) for x in data]
        return tokenized
    
    def make_embeddings(self, tokenized_data):
        result = []

        for sent in tqdm_notebook(tokenized_data):
            result.append(self.model(sent)[0].mean(dim=1).detach().cpu())

        return result

    def write_matrix(self, data, filename='embeddings'):
        mat = np.matrix([x.tolist()[0] for x in data])
        mat.dump(f'drive/MyDrive/competitions/generate_phrases/data/{filename}.dat')

    def run(self, path_or_word_list, output_filename='embeddings'):
        if type(path_or_word_list) == list:
            assert len(path_or_word_list) > 0, "Empty list of words"
            assert type(path_or_word_list[0]) == str, "Wrong type: str expected, found {}".format(type(path_or_word_list[0]))
            self.words = path_or_word_list
        else:
            assert type(path_or_word_list) == str, "Wrong type: str expected, found {}".format(type(path_or_word_list))
            with open(f"drive/MyDrive/competitions/generate_phrases/data/{path_or_word_list}", "r") as f:
                self.words = [x[:-1] for x in f.readlines()]
        
        print("Process started")

        self.tokenized = self.tokenize(self.words)
        print("Tokenized successfully")

        print("Counting embeddings...")
        self.embeddings = self.make_embeddings(self.tokenized)
        print("Counted successfully")

        print("Saving matrix...")
        self.write_matrix(self.embeddings, output_filename)

        print("Done")

    def get_phrase_embedding(self, phrase):
        tokenized = self.tokenize([phrase])
        embedding = self.make_embeddings(tokenized)

        return embedding[0]
        
    def get_by_index(self, index):
        assert self.words is not None, "First specify `words`"

        if type(index) == int:
            index = [index]
        result = []
        for idx in index:
            result.append(self.words[idx])

        return result

class QuestionFinder:
    def __init__(self, embeddings_path_or_matrix):
        '''For usage examples go to ~/junk/run_this_all.ipynb'''
        self.embeddings = None
        if type(embeddings_path_or_matrix) == str:
            self.embeddings = np.load(
                f'drive/MyDrive/competitions/generate_phrases/data/{embeddings_path_or_matrix}.dat',
                 allow_pickle=True
            )
        else:
            self.embeddings = embeddings_path_or_matrix

        self.num = self.embeddings.shape[0]
        self.dim = self.embeddings.shape[1]

        self.labels = np.arange(self.num)

        self.p = hnsw.Index(space='cosine', dim=self.dim)

        # Initializing index - the maximum number of elements should be known beforehand
        self.p.init_index(max_elements=self.num)

        # Element insertion (can be called several times):
        self.p.add_items(self.embeddings, self.labels)

        # Controlling the recall by setting ef:
        self.p.set_ef(50) # ef should always be > k

        # self.closest, self.distances = self.p.knn_query(self.embeddings, k=self.num_neighbours)
    
    def find_closest(self, embedding, num_neighbours=1, remoteness=0):
        closest, distances = self.p.knn_query(embedding, k=num_neighbours + remoteness)
        return closest[0][remoteness:num_neighbours + remoteness]
