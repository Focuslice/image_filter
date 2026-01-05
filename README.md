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
```mermaid
graph TD
    subgraph Host["Host Machine"]
        Client[Client / Request]
        
        subgraph Docker["Container (nsfw-filter-app)"]
            FastAPI[FastAPI App]
            Uvicorn[Uvicorn Server]
            Logic[Inference Logic]
        end
        
        Volume[("Docker Volume<br/>(Model Cache)")]
    end

    Client -->|HTTP POST| Uvicorn
    Uvicorn --> FastAPI
    FastAPI --> Logic
    Logic <-->|Load Model| Volume
    ```