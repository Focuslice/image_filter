from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
import io
from nsfw_filter.nsfw_filter import Nsfw_filter

nsfw_filter = Nsfw_filter()
nsfw_filter.load_model()

app = FastAPI(title="image Image Filter API")

@app.post("/check-image")
async def check_image(file: UploadFile = File(...)):
    if not nsfw_filter.classifier:
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
    results = nsfw_filter.predict_image(image)
    
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