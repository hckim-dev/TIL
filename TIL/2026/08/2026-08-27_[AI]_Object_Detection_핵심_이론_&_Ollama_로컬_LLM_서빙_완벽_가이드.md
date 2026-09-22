# \[AI\] Object Detection 핵심 이론 &amp; Ollama 로컬 LLM 서빙 완벽 가이드

> 날짜: 2026-08-27
> 원본 노션: [링크](https://app.notion.com/p/AI-Object-Detection-Ollama-LLM-3c81d46c18fc80f7b41bf33f0d60c7a9)

<!-- notion-page-id: 3c81d46c18fc80f7b41bf33f0d60c7a9 -->
<!-- notion-title: "[AI] Object Detection 핵심 이론 & Ollama 로컬 LLM 서빙 완벽 가이드" -->

---

<a id="notion-3c81d46c18fc80d58fb1e18e8d967137"></a>

# 🎯 Object Detection (객체 검출) 완벽 정리

<a id="notion-3c81d46c18fc8073b58fde2a3758cd60"></a>

## 1\. Object Detection이란?

컴퓨터 비전(Computer Vision) 분야에서 이미지나 비디오 내에 존재하는 **특정 객체의 위치(Where)를 찾아내고, 해당 객체가 무엇인지(What) 분류**하는 딥러닝 기술입니다.

- **핵심 연산의 결합:**

  - **Classification (분류):** "이 객체는 고양이다/사람이다" (What)
  - **Localization (위치 추정):** "이 객체는 화면의 $(x, y, w, h)$ 좌표에 있다" (Where)
  - **Object Detection:** 1개 이상의 객체에 대해 **Classification + Localization**을 동시 수행

<a id="notion-3c81d46c18fc80c99d79f2660274805e"></a>

### 📌 Computer Vision 핵심 태스크 비교

|  |  |  |
| --- | --- | --- |
| **태스크** | **예측 대상** | **출력 형태** |
| **Image Classification** | 이미지 전체의 단일 라벨 | Class 확률 |
| **Object Detection** | 여러 객체의 위치와 종류 | <strong>Bounding Box</strong> **$(x, y, w, h)$** <strong>\+ Class 확률</strong> |
| **Semantic Segmentation** | 모든 픽셀의 의미적 라벨 (객체 구분 X) | 픽셀 단위 마스크 |
| **Instance Segmentation** | 개별 객체 단위의 위치 + 픽셀 마스크 | Bounding Box + 픽셀 단위 마스크 |

<a id="notion-3c81d46c18fc80aea301f51d1492052f"></a>

## 2\. 필수 핵심 용어 및 개념

- **Bounding Box (BBox):**

  - 검출된 객체를 감싸는 직사각형 박스입니다.
  - 표현 방식: `[x_min, y_min, x_max, y_max]` 또는 `[center_x, center_y, width, height]`.
- **IoU (Intersection over Union, 교집합/합집합 비율):**

  - 모델이 예측한 박스($A$)와 실제 정답 박스($B$, Ground Truth)가 얼마나 겹치는지 측정하는 지표입니다 ($0.0 \sim 1.0$).

    $\text{IoU} = \frac{\text{Area of Overlap }(A \cap B)}{\text{Area of Union }(A \cup B)}$
  - 보통 $\text{IoU} \ge 0.5$ 이상이면 올바르게 검출(True Positive)한 것으로 간주합니다.
- **Confidence Score (신뢰도 점수):**

  - 해당 박스 안에 특정 클래스의 객체가 실제로 존재할 확률 ($0.0 \sim 1.0$).
- **NMS (Non-Maximum Suppression, 비최대 억제):**

  - 동일한 객체 하나에 대해 수많은 중복 박스가 생성되었을 때, **가장 높은 Confidence를 가진 박스만 남기고 겹치는 나머지 박스들을 제거**하는 후처리 알고리즘입니다.
- **mAP (mean Average Precision):**

  - Object Detection 모델의 전체적인 검출 성능을 나타내는 표준 평가지표입니다.
  - 각 클래스별 Precision-Recall 곡선 아래 면적인 AP(Average Precision)를 구한 뒤, 전 클래스에 대해 평균을 낸 값입니다 (예: mAP@0.5, mAP@0.5:0.95).

<a id="notion-3c81d46c18fc805694b2da5a5a39ec3f"></a>

## 3\. 대표적인 모델 계열 비교 (1-Stage vs 2-Stage)

Object Detection 알고리즘은 크게 **2-Stage Detector**와 **1-Stage Detector**로 나뉩니다.

```text
[ Object Detection ]
  ├── 2-Stage Detector (정확도 중심) ──> [위치 후보 추출(RPN)] ➔ [분류 및 좌표 보정]
  │     └── R-CNN ➔ Fast R-CNN ➔ Faster R-CNN ➔ Mask R-CNN
  │
  └── 1-Stage Detector (속도/실시간성 중심) ──> [특징 맵에서 위치와 분류를 동시에 추론]
        └── YOLO Series (v1 ~ v11), SSD, RetinaNet
```

|  |  |  |
| --- | --- | --- |
| **비교 항목** | **2-Stage Detector (예: Faster R-CNN)** | **1-Stage Detector (예: YOLO, SSD)** |
| **동작 방식** | 1단계: RPN으로 후보 영역(RoI) 추출<br><br>2단계: 후보 영역별 분류 및 BBox 보정 | 별도 영역 제안 없이 전체 이미지를 그리드로 나눠 위치와 클래스를 한 번에 예측 |
| **추론 속도** | 상대적으로 느림 (5 \~ 15 FPS) | **매우 빠름 (30 \~ 100+ FPS, 실시간 구동)** |
| **검출 정확도** | 미세 객체 검출에 유리 (높은 mAP) | 초기엔 낮았으나 최신 YOLO 계열은 2-Stage를 능가 |
| **주요 활용처** | 의료 영상 분석, 정밀 불량 검사 | **자율주행, 실시간 CCTV, 엣지(Jetson/모바일) 비전 AI** |

<a id="notion-3c81d46c18fc8007a799f1c6ff3c2520"></a>

## 4\. 데이터셋 포맷 표준 3대장

Object Detection 학습을 위해 라벨링된 어노테이션(Annotation) 파일의 대표적인 포맷입니다.

- <strong>1\) YOLO Format (</strong><strong>`.txt`</strong><strong>)</strong>

  - 이미지 1장당 동일한 이름의 텍스트 파일 1개 매핑.
  - 정규화된 좌표계 ($0.0 \sim 1.0$): `<class_id> <center_x> <center_y> <width> <height>`
- <strong>2\) Pascal VOC Format (</strong><strong>`.xml`</strong><strong>)</strong>

  - 이미지 1장당 XML 파일 1개 매핑.
  - 픽셀 절대 좌표계: `<bndbox> <xmin> <ymin> <xmax> <ymax> </bndbox>`
- <strong>3\) MS COCO Format (</strong><strong>`.json`</strong><strong>)</strong>

  - 전체 데이터셋(Train/Val)의 모든 이미지와 BBox 정보가 단 하나의 큰 JSON 파일에 구조화되어 저장.

<a id="notion-3c81d46c18fc80518b8ec965114a6504"></a>

## 5\. 엣지 디바이스(Jetson) 실무 적용 파이프라인

1. **데이터 준비 및 라벨링:** Roboflow / LabelImg / CVAT 등을 활용해 Bounding Box 라벨링 (YOLO 포맷 권장).
2. **백본 &amp; 모델 학습:** PyTorch 기반 최신 YOLO (YOLOv8 / YOLOv11 등) 모델 학습.
3. **ONNX 변환 &amp; 단순화:** NMS 후처리 노드를 포함하거나 분리하여 `model.onnx`로 export 후 `onnxsim` 최적화.
4. **TensorRT 엔진 빌드:** 젯슨 보드에서 `trtexec --onnx=model.onnx --saveEngine=model.engine --fp16` 실행.
5. **Zero-Copy 실시간 추론:** 카메라 스트림을 입력받아 GPU 추론 후 NMS 필터링을 거쳐 화면에 BBox/라벨 렌더링.

<a id="notion-3c91d46c18fc80e18761f94bf56a0768"></a>

# 🦙 Ollama 완벽 정리: 설치부터 Python SDK까지

<a id="notion-3c91d46c18fc80c0b92ac85e03ae58fc"></a>

### 1\. Ollama란?

- **개념:** 대규모 언어 모델(LLM)을 로컬 환경(PC, Jetson 등)에서 손쉽게 다운로드, 최적화 및 서빙할 수 있도록 지원하는 **오픈소스(MIT 라이선스) 경량 런타임 프레임워크**.
- **비용:** \$0 (완전 무료 및 오프라인 구동 가능, 토큰 비용 없음).
- **특징:**

  - llama.cpp 기반의 고효율 양자화(4-bit, 8-bit 등) 모델 가속 구동.
  - 로컬 REST API 서버 자동 제공 (기본 포트: `11434`).
  - Docker, Python/JS SDK 및 Open WebUI와의 손쉬운 연동 지원.

<a id="notion-3c91d46c18fc807b91d1f4b566615cb3"></a>

### 2\. 주요 CLI 명령어 치트시트

|  |  |  |
| --- | --- | --- |
| **명령어** | **설명** | **예시** |
| `ollama run <모델명>` | 모델 다운로드 및 대화형 CLI 세션 실행 | `ollama run qwen2.5:3b` |
| `ollama pull <모델명>` | 모델 사전 다운로드만 진행 (실행 X) | `ollama pull llama3.2:1b` |
| `ollama list` | 로컬에 설치된 모델 목록 및 크기 확인 | `ollama list` |
| `ollama ps` | 현재 메모리(VRAM/RAM)에 로드된 모델 확인 | `ollama ps` |
| `ollama rm <모델명>` | 설치된 모델 삭제 | `ollama rm gemma2:2b` |

<a id="notion-3c91d46c18fc806ebfbbc01e0d087adf"></a>

### 3\. 소형 모델(SLM) 추천 및 리소스 비교 (Jetson / 로컬 PC)

|  |  |  |  |
| --- | --- | --- | --- |
| **모델명** | **파라미터** | **메모리 점유 (Q4)** | **특징 및 주 활용처** |
| **`qwen2.5:3b`** | 3.09B | 약 2.0GB \~ 2.3GB | **종합 추천 1위** (한국어 구사력 최상, Tool Calling / JSON 완벽 지원) |
| **`qwen2.5:1.5b`** | 1.54B | 약 1.0GB \~ 1.2GB | 초경량 리소스 절약형 (비전 엔진 등 다른 태스크와 동시 실행 시 추천) |
| **`llama3.2:3b`** | 3.21B | 약 2.2GB \~ 2.5GB | 지시 이행(Instruction Following) 및 요약/일반 대화 강점 |
| **`llama3.2:1b`** | 1.23B | 약 0.8GB \~ 0.9GB | 백그라운드 에이전트 및 초저지연 연산 |

<a id="notion-3c91d46c18fc80f89f58f4e6ddca6b3e"></a>

### 4\. Python SDK 활용 가이드

<a id="notion-3c91d46c18fc806f84d4f0eb8adb1f83"></a>

#### 4.1. 설치

```bash
pip install ollama
```

<a id="notion-3c91d46c18fc80d2a1d1e0bc9a9f56cb"></a>

#### 4.2. 기본 질의 코드 (`ollama.chat` 표준 인터페이스)

> `ollama.generate`보다 `ollama.chat`이 시스템/사용자 역할을 명확히 구분하는 최신 Chat Template 표준입니다.

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

<a id="notion-3c91d46c18fc8027ad60fb72f8762dd3"></a>

#### 4.3. 실시간 스트리밍 출력 (Streaming)

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

<a id="notion-3c91d46c18fc803a9393ccbf9061c11d"></a>

### 5\. Open WebUI (Docker)

- **Docker 백그라운드 실행:**

  ```bash
  docker run -d \
    --network=host \
    -v open-webui:/app/backend/data \
    -e OLLAMA_BASE_URL=http://127.0.0.1:11434 \
    --name open-webui \
    --restart always \
    ghcr.io/open-webui/open-webui:main
  ```
- **컨테이너 중지:** `docker stop open-webui`

<br>
