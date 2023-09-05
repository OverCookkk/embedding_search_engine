import sys

from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
from config import MODEL_PATH
import gdown
import zipfile
import os

sys.path.append('../')
from config import MODEL_PATH


class SentenceModel:
    """
    paraphrase-mpnet-base-v2是基于BERT（Bidirectional Encoder Representations from Transformers）的模型，用于进行句子重述（paraphrasing）任务。它是通过在大规模文本语料库上进行预训练而得到的，具有深度的双向Transformer结构。
    该模型的目标是将输入的句子转化为与原始句子意思相似但表达方式不同的句子。它可以用于多种自然语言处理任务，如问答系统、文本摘要、机器翻译等，以及一些应用领域，如信息检索和文本生成。
    paraphrase-mpnet-base-v2模型在预训练阶段使用了大量的无监督数据，通过学习上下文关系和语义表示来捕捉句子之间的相似性。在具体任务中，可以通过微调（fine-tuning）这个模型来适应特定的句子重述任务，并提供更准确的结果。
    """

    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            os.makedirs(MODEL_PATH)
        if not os.path.exists("./paraphrase-mpnet-base-v2.zip"):
            url = 'https://public.ukp.informatik.tu-darmstadt.de/reimers/sentence-transformers/v0.2/paraphrase-mpnet-base-v2.zip'
            gdown.download(url)
        with zipfile.ZipFile('paraphrase-mpnet-base-v2.zip', 'r') as zip_ref:
            zip_ref.extractall(MODEL_PATH)
        self.model = SentenceTransformer(MODEL_PATH)

    def sentence_encode(self, data):
        embedding = self.model.encode(data)
        sentence_embeddings = normalize(embedding)
        return sentence_embeddings.tolist()
