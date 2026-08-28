# [AI] Object Detection 핵심 이론 & Ollama 로컬 LLM 서빙 완벽 가이드

> 날짜: 2026-08-27
> 원본 노션: [링크](https://app.notion.com/p/AI-Object-Detection-Ollama-LLM-3c81d46c18fc80f7b41bf33f0d60c7a9)

---

# 🎯 Object Detection (객체 검출) 완벽 정리

## 1. Object Detection이란?

컴퓨터 비전(Computer Vision) 분야에서 이미지나 비디오 내에 존재하는 특정 객체의 위치(Where)를 찾아내고, 해당 객체가 무엇인지(What) 분류하는 딥러닝 기술입니다.

- 핵심 연산의 결합:
### 📌 Computer Vision 핵심 태스크 비교

| 태스크 | 예측 대상 | 출력 형태 |
|---|---|---|
| Image Classification | 이미지 전체의 단일 라벨 | Class 확률 |
| Object Detection | 여러 객체의 위치와 종류 | Bounding Box (x, y, w, h) + Class 확률 |
| Semantic Segmentation | 모든 픽셀의 의미적 라벨 (객체 구분 X) | 픽셀 단위 마스크 |
| Instance Segmentation | 개별 객체 단위의 위치 + 픽셀 마스크 | Bounding Box + 픽셀 단위 마스크 |

## 2. 필수 핵심 용어 및 개념

- Bounding Box (BBox):
- IoU (Intersection over Union, 교집합/합집합 비율):
- Confidence Score (신뢰도 점수):
- NMS (Non-Maximum Suppression, 비최대 억제):
- mAP (mean Average Precision):
## 3. 대표적인 모델 계열 비교 (1-Stage vs 2-Stage)

Object Detection 알고리즘은 크게 2-Stage Detector와 1-Stage Detector로 나뉩니다.

```plain text
[ Object Detection ]
  ├── 2-Stage Detector (정확도 중심) ──> [위치 후보 추출(RPN)] ➔ [분류 및 좌표 보정]
  │     └── R-CNN ➔ Fast R-CNN ➔ Faster R-CNN ➔ Mask R-CNN
  │
  └── 1-Stage Detector (속도/실시간성 중심) ──> [특징 맵에서 위치와 분류를 동시에 추론]
        └── YOLO Series (v1 ~ v11), SSD, RetinaNet
```

| 비교 항목 | 2-Stage Detector (예: Faster R-CNN) | 1-Stage Detector (예: YOLO, SSD) |
|---|---|---|
| 동작 방식 | 1단계: RPN으로 후보 영역(RoI) 추출<br><br>2단계: 후보 영역별 분류 및 BBox 보정 | 별도 영역 제안 없이 전체 이미지를 그리드로 나눠 위치와 클래스를 한 번에 예측 |
| 추론 속도 | 상대적으로 느림 (5 ~ 15 FPS) | 매우 빠름 (30 ~ 100+ FPS, 실시간 구동) |
| 검출 정확도 | 미세 객체 검출에 유리 (높은 mAP) | 초기엔 낮았으나 최신 YOLO 계열은 2-Stage를 능가 |
| 주요 활용처 | 의료 영상 분석, 정밀 불량 검사 | 자율주행, 실시간 CCTV, 엣지(Jetson/모바일) 비전 AI |

## 4. 데이터셋 포맷 표준 3대장

Object Detection 학습을 위해 라벨링된 어노테이션(Annotation) 파일의 대표적인 포맷입니다.

- 1) YOLO Format (.txt)
- 2) Pascal VOC Format (.xml)
- 3) MS COCO Format (.json)
## 5. 엣지 디바이스(Jetson) 실무 적용 파이프라인

1. 데이터 준비 및 라벨링: Roboflow / LabelImg / CVAT 등을 활용해 Bounding Box 라벨링 (YOLO 포맷 권장).
1. 백본 & 모델 학습: PyTorch 기반 최신 YOLO (YOLOv8 / YOLOv11 등) 모델 학습.
1. ONNX 변환 & 단순화: NMS 후처리 노드를 포함하거나 분리하여 model.onnx로 export 후 onnxsim 최적화.
1. TensorRT 엔진 빌드: 젯슨 보드에서 trtexec --onnx=model.onnx --saveEngine=model.engine --fp16 실행.
1. Zero-Copy 실시간 추론: 카메라 스트림을 입력받아 GPU 추론 후 NMS 필터링을 거쳐 화면에 BBox/라벨 렌더링.
# 🦙 Ollama 완벽 정리: 설치부터 Python SDK까지

### 1. Ollama란?

- 개념: 대규모 언어 모델(LLM)을 로컬 환경(PC, Jetson 등)에서 손쉽게 다운로드, 최적화 및 서빙할 수 있도록 지원하는 오픈소스(MIT 라이선스) 경량 런타임 프레임워크.
- 비용: $0 (완전 무료 및 오프라인 구동 가능, 토큰 비용 없음).
- 특징:
### 2. 주요 CLI 명령어 치트시트

| 명령어 | 설명 | 예시 |
|---|---|---|
| ollama run <모델명> | 모델 다운로드 및 대화형 CLI 세션 실행 | ollama run qwen2.5:3b |
| ollama pull <모델명> | 모델 사전 다운로드만 진행 (실행 X) | ollama pull llama3.2:1b |
| ollama list | 로컬에 설치된 모델 목록 및 크기 확인 | ollama list |
| ollama ps | 현재 메모리(VRAM/RAM)에 로드된 모델 확인 | ollama ps |
| ollama rm <모델명> | 설치된 모델 삭제 | ollama rm gemma2:2b |

### 3. 소형 모델(SLM) 추천 및 리소스 비교 (Jetson / 로컬 PC)

| 모델명 | 파라미터 | 메모리 점유 (Q4) | 특징 및 주 활용처 |
|---|---|---|---|
| qwen2.5:3b | 3.09B | 약 2.0GB ~ 2.3GB | 종합 추천 1위 (한국어 구사력 최상, Tool Calling / JSON 완벽 지원) |
| qwen2.5:1.5b | 1.54B | 약 1.0GB ~ 1.2GB | 초경량 리소스 절약형 (비전 엔진 등 다른 태스크와 동시 실행 시 추천) |
| llama3.2:3b | 3.21B | 약 2.2GB ~ 2.5GB | 지시 이행(Instruction Following) 및 요약/일반 대화 강점 |
| llama3.2:1b | 1.23B | 약 0.8GB ~ 0.9GB | 백그라운드 에이전트 및 초저지연 연산 |

### 4. Python SDK 활용 가이드

```bash
pip install ollama
```

> ollama.generate보다 ollama.chat이 시스템/사용자 역할을 명확히 구분하는 최신 Chat Template 표준입니다.

```python
import ollama


def ask_llm(prompt: str, model: str = "qwen2.5:3b") -> str:
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],  #
            options={"temperature": 0.7},
        )
        return response.message.content or ""  #
    except ollama.ResponseError as e:
        print(f"❌ Ollama 오류 [{e.status_code}]: {e.error}")
        return ""
    except ConnectionError:
        print("❌ Ollama 서비스가 실행 중인지 확인하세요 (11434 포트)")
        return ""


if __name__ == "__main__":
    answer = ask_llm("왜 하늘은 파란색이야? 한 줄로 답해줘.")
    print(answer)
```

```python
import ollama

stream = ollama.chat(
    model="qwen2.5:3b",
    messages=[{"role": "user", "content": "양자역학의 기본 개념을 설명해줘."}],  #
    stream=True,  #
)

for chunk in stream:  #
    print(chunk["message"]["content"], end="", flush=True)  #
```

### 5. Open WebUI (Docker)

- Docker 백그라운드 실행:
- 컨테이너 중지: docker stop open-webui


