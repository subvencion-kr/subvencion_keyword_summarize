from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from konlpy.tag import Okt
from collections import Counter
from keybert import KeyBERT
from kiwipiepy import Kiwi
from transformers import BertModel
from textrankr import TextRank

app = FastAPI()

class OktTokenizer:
    okt: Okt = Okt()
    def __call__(self, text:str) -> List[str]:
        tokens: List[str] = self.okt.phrases(text)
        return tokens
tokenizer: OktTokenizer = OktTokenizer()
textrank: TextRank = TextRank(tokenizer)

# 형태소 분석기와 키워드 모델 초기화
okt = Okt()
kiwi = Kiwi()
bert_model = BertModel.from_pretrained('skt/kobert-base-v1')
kw_model = KeyBERT(bert_model)
## textrank ·= TextRank(///)

# 요청 데이터의 스키마 정의
class WelfareInfo(BaseModel):
    _id: Optional[Dict[str, str]]  # MongoDB ObjectId
    serviceId: str
    supportType: str
    serviceName: str
    servicePurpose: Optional[str]
    applicationDeadline: Optional[str]
    targetGroup: Optional[str]
    selectionCriteria: Optional[str]
    supportDetails: Optional[str]
    applicationMethod: Optional[str]
    requiredDocuments: Optional[str]
    receptionInstitutionName: Optional[str]
    contactInfo: Optional[str]
    responsibleInstitutionName: Optional[str]
    supportCondition: Optional[List[str]]

class SummarizeInfo(BaseModel):
    content: str
    serviceId: str

# 키워드 추출 함수
def extract_keywords(text: str, num_keywords: int = 20) -> List[str]:
    nouns = okt.nouns(text)
    count = Counter(nouns)
    keywords = [word for word, _ in count.most_common(num_keywords)]
    return keywords

# 키워드 추출 엔드포인트
@app.post("/extract_keywords/", response_model=List[str])
async def extract_keywords_from_welfare(data: WelfareInfo):
    try:
        # 분석할 텍스트 조합
        text_to_analyze = ' '.join([
            data.serviceName,
            data.supportType,
            data.servicePurpose or '',
            data.targetGroup or '',
            data.selectionCriteria or '',
            data.supportDetails or ''
        ])
        
        # 키워드 추출
        keywords = kw_model.extract_keywords(text_to_analyze, keyphrase_ngram_range=(1, 1), stop_words=None, top_n=20)
        keyword_list = ' '.join([word for word, _ in keywords])
        return keyword_list.split()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 요약 생성 엔드포인트
@app.post("/summarize_welfare/", response_model=str)
async def summarize_welfare(data: SummarizeInfo):
    try:
        summaries = textrank.summarize(data.content, 3, verbose=False)
        return "\n".join(summaries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 테스트용 API 확인 엔드포인트
@app.get("/")
def read_root():
    return {"message": "Welfare Keyword and Summary API"}

# 서버 실행을 위한 main 함수 (uvicorn으로 실행)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=23500)