# Image_filter
## 설명
이미지의 선정성, 폭력성, 혐오성 컨텐츠가 존재하는지 필터링하는 api입니다.

## 사용방법
```bash
git clone https://github.com/Focuslice/image_filter.git
# git 서브모듈까지 업데이트
git submodule update --init --recursive

docker build -t {image 이름} .
docker run -d -p 8000:8000 --name {컨테이너 이름} {이미지 이름}
```

## 아키텍처
```mermaid
sequenceDiagram
    participant User as Client (User)
    participant API as FastAPI Server
    participant Logic as Image Processor (PIL)
    participant Model as AI Model (ViT)

    User->>API: POST /predict (Image)
    activate API
    
    API->>API: 파일 형식 검증 (JPG/PNG)
    alt 형식이 잘못됨
        API-->>User: 400 Error (Invalid File)
    else 형식이 올바름
        API->>Logic: 이미지 바이트 변환 & 리사이징
        activate Logic
        Logic-->>API: 전처리된 이미지 객체
        deactivate Logic
        
        API->>Model: 추론 요청 (Inference)
        activate Model
        Model-->>API: 결과 반환 ({label: 'nsfw', score: 0.99})
        deactivate Model
        
        API->>API: 임계값 비교 (Score > 0.8?)
        API-->>User: 200 OK (is_toxic: true)
    end
    deactivate API
```