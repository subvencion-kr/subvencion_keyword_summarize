from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from konlpy.tag import Okt
from collections import Counter

app = FastAPI()

# 형태소 분석기 초기화
okt = Okt()

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

# 키워드 추출 함수
def extract_keywords(text: str, num_keywords: int = 20) -> List[str]:
    nouns = okt.nouns(text)
    count = Counter(nouns)
    keywords = [word for word, _ in count.most_common(num_keywords)]
    return keywords

# 요약 생성 함수
def summarize_welfare_data(welfare_data: WelfareInfo) -> str:
    summary_parts = [
        f"서비스명: {welfare_data.serviceName}",
        f"목적: {welfare_data.servicePurpose or '정보 없음'}",
        f"대상: {welfare_data.targetGroup or '정보 없음'}",
        f"지원 내용: {welfare_data.supportDetails or '정보 없음'}",
        f"신청 마감일: {welfare_data.applicationDeadline or '정보 없음'}"
    ]
    return "\n".join(summary_parts)

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
        keywords = extract_keywords(text_to_analyze)
        return keywords
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 요약 생성 엔드포인트
@app.post("/summarize_welfare/", response_model=str)
async def summarize_welfare(data: WelfareInfo):
    try:
        # 요약 생성
        summary = summarize_welfare_data(data)
        return summary
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
