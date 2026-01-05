from fastapi import FastAPI, UploadFile, File, HTTPException
from transformers import pipeline
from PIL import Image
import io

app = FastAPI(title="NSFW Filter API (Dockerized)")

# 전역 변수로 모델 선언
classifier = None

@app.on_event("startup")
async def load_model():
    """서버 시작 시 모델을 로드합니다."""
    global classifier
    print("Loading AI Model... (This may take a while for the first time)")
    try:
        # 모델은 docker-compose에 정의된 볼륨 경로에 저장됩니다.
        classifier = pipeline("image-classification", model="Falconsai/nsfw_image_detection")
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Failed to load model: {e}")

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model is not ready yet.")

    # 파일 형식 검증
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Only JPEG/PNG supported.")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    # 추론 수행
    results = classifier(image)
    
    # 결과 해석 (nsfw 점수 추출)
    # results 예시: [{'label': 'nsfw', 'score': 0.99}, {'label': 'normal', 'score': 0.01}]
    nsfw_prob = 0.0
    for res in results:
        if res['label'] == 'nsfw':
            nsfw_prob = res['score']
    
    # 임계값 설정 (예: 0.8 이상이면 차단)
    is_toxic = nsfw_prob > 0.8

    return {
        "filename": file.filename,
        "is_toxic": is_toxic,
        "nsfw_probability": round(nsfw_prob, 4),
        "raw_result": results
    }