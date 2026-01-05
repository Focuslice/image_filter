from fastapi import FastAPI, UploadFile, File, HTTPException
from transformers import pipeline
from PIL import Image
import io

app = FastAPI(title="NSFW Image Filter API")

# 1. 모델 로드 (서버 시작 시 한 번만 로드하여 메모리에 상주)
# 'falconsai/nsfw_image_detection'은 Hugging Face에서 인기 있는 모델 중 하나입니다.
# 폭력성 등 더 다양한 카테고리가 필요하면 다른 모델로 교체 가능합니다.
try:
    classifier = pipeline("image-classification", model="Falconsai/nsfw_image_detection")
except Exception as e:
    print(f"모델 로드 실패: {e}")
    classifier = None

@app.post("/check-image")
async def check_image(file: UploadFile = File(...)):
    if not classifier:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # 2. 이미지 유효성 검사 및 로드
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG images are allowed.")
    
    try:
        # 업로드된 파일을 메모리에서 읽어 PIL 이미지로 변환
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    # 3. 모델 추론 (Inference)
    results = classifier(image)
    
    # 4. 결과 파싱 (NSFW 확률 계산)
    # 결과 예시: [{'label': 'nsfw', 'score': 0.98}, {'label': 'normal', 'score': 0.02}]
    nsfw_score = 0.0
    for result in results:
        if result['label'] == 'nsfw':
            nsfw_score = result['score']
            break
            
    # 5. 정책 결정 (임계값 설정)
    # 0.8(80%) 이상이면 차단 등으로 설정
    is_unsafe = nsfw_score > 0.8
    
    return {
        "filename": file.filename,
        "is_unsafe": is_unsafe,
        "nsfw_score": round(nsfw_score, 4),
        "detail": results
    }

# 실행 명령: uvicorn main:app --reload