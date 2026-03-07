import os
from typing import List, Dict, Any
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv

load_dotenv()

class AzureSearchService:
    """
    محرك البحث في البيانات (RAG) لخدمة megabot
    متوافق مع Azure AI Search Free Tier
    """
    
    def __init__(self, index_name: str = "antigravity-index"):
        self.endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
        self.api_key = os.getenv("AZURE_AI_SEARCH_KEY")
        self.index_name = index_name
        
        if not self.endpoint or not self.api_key:
            print("[WARN] Azure Search credentials missing. RAG service disabled.")
            self.client = None
        else:
            self.client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.index_name,
                credential=AzureKeyCredential(self.api_key)
            )
            print(f"[OK] Azure Search connected to: {self.endpoint}")

    async def find_relevant_data(self, query: str, top: int = 3) -> str:
        """
        البحث عن معلومات متعلقة بالطلب (مثلاً أذكار معينة أو بيانات عميل)
        """
        if not self.client:
            return ""

        try:
            results = self.client.search(search_text=query, top=top)
            context = "\nالمعلومات المستخرجة من قاعدة البيانات:\n"
            found = False
            
            for result in results:
                found = True
                # بنفترض إن الحقول اسمها content و source
                context += f"- {result.get('content', '')} (المصدر: {result.get('source', 'غير معروف')})\n"
            
            return context if found else ""
            
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            return ""
