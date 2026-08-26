# [AI] 딥러닝 학습부터 젯슨(Jetson) TensorRT Zero-Copy 실시간 배포까지 End-to-End 파이프라인 완벽 가이드

> 날짜: 2026-08-26
> 원본 노션: [링크](https://app.notion.com/p/AI-Jetson-TensorRT-Zero-Copy-End-to-End-3c71d46c18fc80069622c3a4f9e942bf)

---

# 🚀 딥러닝 End-to-End MLOps 파이프라인 총정리

전체 흐름은 [데이터 준비] -> [모델 학습] -> [네이티브 저장] -> [ONNX 변환] -> [그래프 최적화(onnxsim)] -> [검증 및 엣지 배포] 순서로 진행됩니다.

```plain text
[1. 데이터 준비] ──(tf.data 고속 파이프라인)──> [2. 전이학습/미세조정]
                                                        │
                                                        ▼
[4. ONNX 변환 (표준 포맷)] <──(추론 모드 저장)── [3. 네이티브 저장 (.keras/.pt)]
        │
        ▼
[5. ONNX 다이어트 (onnxsim)] ──> [6. 수치 검증 (onnxruntime)] ──> [7. 엣지 배포 (TensorRT)]
```

## 1단계. 데이터 준비 및 초고속 I/O 파이프라인

> 핵심 목표: GPU가 연산하는 동안 놀지(Idle) 않도록 CPU가 데이터를 끊김 없이 전달하는 파이프라인 구축

- 데이터 분할: Train(학습용 70~80%), Validation(검증용 10~20%), Test(최종 평가용 10%)
- 데이터 증강 (Augmentation): 사진을 무작위로 뒤집고 회전시켜 모델이 다양한 각도에서도 잘 맞추도록 훈련 (과적합 방지)
- 초고속 I/O 최적화 3요소:
## 2단계. 전이학습(Transfer Learning) 2-Step 전략

> 핵심 목표: 처음부터 다 학습하지 않고 이미 똑똑한 사전학습 모델(MobileNet, ResNet 등)을 가져와 내 데이터에 맞춤 튜닝

```plain text
[입력 이미지] ──> [데이터 증강/정규화] ──> [사전학습 백본 (Frozen)] ──> [새로운 분류기 (Head)]
```

- Step A. 특징 추출기 동결 (Feature Extraction):
- Step B. 미세 조정 (Fine-Tuning):
## 3단계. 똑똑한 학습 제어 (Callbacks) & 모델 저장

> 핵심 목표: 과적합이 오면 알아서 멈추고, 가장 성적이 좋았던 순간의 가중치만 저장

- 손실 함수 & 옵티마이저: sparse_categorical_crossentropy(다중 분류) + Adam/AdamW
- 필수 3대 콜백 함수:
- 네이티브 포맷 저장:
## 4단계. ONNX 변환 (만국 공용 딥러닝 포맷)

> 핵심 개념: 한글/워드 문서를 누구나 열어볼 수 있는 PDF로 바꾸듯, Keras/PyTorch 모델을 모든 플랫폼에서 구동 가능한 **.onnx**로 변환

### Python 코드로 Keras -> ONNX 변환

```python
import tensorflow as tf
import tf2onnx

model = tf.keras.models.load_model("best_model.keras")

# 입력 규격(Signature) 정의: (배치크기 가변, 224, 224, 3)
spec = [
    tf.TensorSpec(shape=(None, 224, 224, 3), dtype=tf.float32, name="input")
]

# ONNX 파일 내보내기
onnx_model, _ = tf2onnx.convert.from_keras(
    model, input_signature=spec, opset=17, output_path="model.onnx"
)
```

### PyTorch -> ONNX 변환

```python
import torch

model.eval()
dummy_input = torch.randn(1, 3, 224, 224)

torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
    opset_version=17,
)
```

## 5단계. ONNX Simplifier (onnxsim)로 그래프 다이어트

> 핵심 목표: 변환 중 발생한 찌꺼기/중복 연산 노드를 제거하여 TensorRT 변환 시 충돌 에러 방지 및 속도 향상

- 상수 폴딩 (Constant Folding): 입력 이미지와 상관없이 고정된 수식 연산(Shape 계산, 축 변환 등)을 변환 시점에 미리 계산해 고정 값으로 박아둠
- 더미 노드 제거: 불필요한 형변환(Cast), 무의미한 복사(Identity) 노드 삭제
```python
import onnx
from onnxsim import simplify

model = onnx.load("model.onnx")
model_simp, check = simplify(model)

if check:
    onnx.save(model_simp, "model_sim.onnx")
    print("그래프 단순화 완료: model_sim.onnx")
```

## 6단계. 수치 무결성 검증 (Verification)

> 핵심 목표: ONNX로 바꿨을 때 원본 모델과 결괏값(출력 텐서)이 동일한지 컴퓨터로 확인

```python
import numpy as np
import onnx
import onnxruntime as ort

# 1. 그래프 무결성 체크
onnx.checker.check_model(onnx.load("model_sim.onnx"))

# 2. ONNX Runtime 가상 추론
session = ort.InferenceSession("model_sim.onnx")
input_name = session.get_inputs()[0].name
dummy_data = np.random.randn(1, 224, 224, 3).astype(np.float32)

outputs = session.run(None, {input_name: dummy_data})
print("추론 성공! 출력 Shape:", outputs[0].shape)
```

## 7단계. 최종 요약 및 엣지 배포 로드맵

| 단계 | 도구 / 포맷 | 핵심 역할 | 실무 체크포인트 |
|---|---|---|---|
| 1. Data I/O | tf.data, Dataset | 고속 데이터 공급 | .prefetch(), .cache()로 GPU 대기시간 제거 |
| 2. Training | Keras / PyTorch | 2-Step 전이학습 | Feature Extractor 동결 후 상위 레이어 미세조정 |
| 3. Export | .keras, .pt | 원본 모델 보관 | EarlyStopping 적용 후 Best Weight 저장 |
| 4. ONNX Convert | tf2onnx, torch.onnx | 공용 포맷 변환 | opset=17, 입출력 Shape 일치 확인 |
| 5. Simplify | onnxsim | 그래프 다이어트 | 중복 연산 제거로 TensorRT 변환 에러 예방 |
| 6. Verification | onnxruntime | 수치 일치 검증 | 원본 모델과 예측 오차(\le 10^{-4}) 확인 |
| 7. Edge Deploy | TensorRT (.engine) | Jetson 하드웨어 가속 | FP16/INT8 양자화 적용으로 FPS 극대화 |

### [확장 파이프라인 전체 흐름]

```plain text
[6. 수치 검증 완료 (onnxruntime)] ──(SCP/SFTP 전송)──> [8. Jetson 보드로 전송]
                                                              │
                                                              ▼
[10. 실시간 비전 배포 (웹캠 + Zero-Copy)] <── [9. TensorRT 엔진 빌드 (trtexec)]
```

### 8단계. Jetson 보드로 최적화 ONNX 전송

PC/Colab 환경에서 검증을 마친 model_sim.onnx 파일을 네트워크를 통해 Jetson 보드의 작업 디렉터리로 복사합니다.

- SCP 명령어로 전송 (PC 터미널):
### 9단계. trtexec를 이용한 TensorRT 엔진(.engine) 컴파일

Jetson의 Orin GPU 아키텍처(Ampere)에 맞춰 하드웨어 최적화 바이너리 파일(.engine)을 생성합니다.

- 기본 정적 Shape 엔진 변환 (FP16 반정밀도 가속):
- 가변 배치(Dynamic Batch) 모델인 경우 (Shape 범위 명시):
- 빌드 성공 확인 체크포인트:
### 10단계. 왜 Jetson에서 굳이 .engine으로 바꿔야 하는가?

ONNX는 '범용 설계도'이고, TensorRT Engine은 '내 젯슨 GPU 맞춤형 기계어'이기 때문입니다.

```plain text
[ ONNX (범용 설계도) ]
       │
       ▼ (trtexec 컴파일 최적화)
       ├─ 레이어 융합 (Layer Fusion): Conv + BatchNorm + ReLU를 1개 커널로 압축
       ├─ FP16 양자화: Jetson Orin의 텐서 코어(Tensor Core) 하드웨어 가속 매핑
       ├─ 커널 자동 튜닝: GPU 메모리 대역폭과 SM 아키텍처에 최적화된 알고리즘 선택
       │
[ TensorRT Engine (.engine) ] ──> 극대화된 FPS와 초저지연(Latency) 달성
```

- 속도 및 성능 (2~5배 향상): ONNX 런타임 대비 텐서 코어를 100% 활용하여 실시간 처리(30~60+ FPS) 가능
- 메모리(VRAM) 절감: FP16 적용 시 모델 가중치 용량 및 점유 메모리가 50% 절감
- Zero-Copy 호환성: Jetson의 CPU-GPU 통합 메모리(Unified Memory) 구조와 결합하여 메모리 복사 지연 없이 다이렉트 추론 가능
### 11단계. 실무 파이썬 배포 연동 (Zero-Copy 기반)

생성된 .engine 파일을 로드하여 웹캠 입력 영상을 실시간으로 분류하는 최종 배포 단계입니다.

```python
import cv2
import numpy as np
from trt_module import TRTInferenceEngine

# 1. 컴파일된 가속 엔진 로드 (Zero-Copy 버퍼 자동 할당)
engine = TRTInferenceEngine("model.engine")

# 2. 웹캠 프레임 캡처 및 전처리
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
ret, frame = cap.read()

# 전처리 (RGB 변환 -> Resize -> 정규화 -> 배치 차원 추가)
img = cv2.cvtColor(
    cv2.resize(frame, (224, 224)), cv2.COLOR_BGR2RGB
).astype(np.float32)
input_data = (img / 255.0)[np.newaxis, ...]

# 3. 비동기 GPU 초고속 추론 (지연 시간 0ms 메모리 매핑)
output = engine.infer(input_data)
predicted_class = int(np.argmax(output))
```

### 📊 최종 배포 파이프라인 요약표 (전체 완결)

| 단계 | 도구 / 포맷 | 핵심 역할 | 실무 체크포인트 |
|---|---|---|---|
| 8. Transfer | scp / SFTP | Jetson 보드로 최적화 모델 전송 | .onnx 파일 누락 없이 타겟 폴더로 복사 |
| 9. TRT Build | trtexec | Jetson Orin 맞춤형 .engine 컴파일 | --fp16 옵션 적용 및 PASSED 로그 확인 |
| 10. Zero-Copy I/O | PyCUDA + Unified Memory | CPU-GPU 간 데이터 복사 지연 제거 | pagelocked_empty(..., DEVICEMAP) 활용 |
| 11. Edge Vision | OpenCV + TensorRT | 실시간 영상 스트림 On-Device AI 구동 | 웹캠 30 FPS 안정적 유지 및 지터링 방지 |

### Zero-Copy란?

CPU와 GPU(또는 OS 커널과 사용자 공간) 사이에서 불필요한 데이터 복사(Memory Copy) 과정을 완전히 없애고(Zero), 동일한 물리 메모리 주소를 직접 공유하여 읽고 쓰는 기술을 말합니다.

```python
# 1. CPU-GPU가 물리 주소를 다이렉트로 공유하는 고정 메모리(Pinned Buffer) 생성
host_mem = cuda.pagelocked_empty(
    size, dtype, mem_flags=cuda.host_alloc_flags.DEVICEMAP
)

# 2. 할당된 물리 메모리의 GPU 하드웨어 버스 주소를 가져옴
device_ptr = host_mem.base.get_device_pointer()

# 3. TensorRT 10.x 엔진에 복사 없이 해당 GPU 물리 주소를 다이렉트 바인딩
self.context.set_tensor_address(tensor_name, int(device_ptr))
```

- 이동 시간 제거: CPU가 데이터를 채워 넣자마자 GPU가 즉시 읽을 수 있어 전송 딜레이(Latency)가 0ms가 됩니다.
- 대역폭 절약: 엣지 장치의 좁은 시스템 버스 통로를 복사 연산으로 막지 않아 시스템 전체 성능이 최적화됩니다.
- 메모리 절약: 같은 프레임을 CPU용, GPU용으로 2번 복제하지 않아 메모리 낭비가 없습니다.
