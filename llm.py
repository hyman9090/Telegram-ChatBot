from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores import FAISS

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import LlamaCpp

from langchain.chains import LLMChain
from langchain.chains.prompt_selector import ConditionalPromptSelector
from langchain.prompts import PromptTemplate

from langchain.chains import RetrievalQA

from pathlib import Path


class LLM:

    def __init__(self, documemt):
        self.root = Path(".")
        self.document = documemt
        self.loader = PyMuPDFLoader(str(self.root / "Documents" / self.document))
        self.loader = self.build_pdf_loader(self.document)

        PDF_data = self.loader.load()

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100, chunk_overlap=5
        )
        self.all_splits = self.text_splitter.split_documents(PDF_data)

        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.model_kwargs = {"device": "cpu"}
        self.embedding = HuggingFaceEmbeddings(
            model_name=self.model_name, model_kwargs=self.model_kwargs
        )

        self.vectordb = FAISS.from_documents(
            documents=self.all_splits, embedding=self.embedding
        )

        self.model_path = str(self.root / "models" / "llama-2-7b-chat.Q4_K_M.gguf")

        self.llm = LlamaCpp(
            model_path=self.model_path,
            n_gpu_layers=100,
            n_batch=512,
            n_ctx=2048,
            f16_kv=True,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            verbose=False,
        )

        self.retriever = self.vectordb.as_retriever()

        self.qa = RetrievalQA.from_chain_type(
            llm=self.llm, chain_type="stuff", retriever=self.retriever, verbose=False
        )

    def build_pdf_loader(self, document):
        return PyMuPDFLoader(str(self.root / "Documents" / document))

    def ask_llm(self, query):
        answer = self.qa.invoke(query)["result"]
        return answer


if __name__ == "__main__":
    llm = LLM("virtual character.pdf")
    answer = llm.ask_llm("Tell me about Alison Hawk's career and age")
    print(answer)
