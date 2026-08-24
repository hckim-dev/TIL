# [AI] CNN 구조와 파이프라인 완벽 정리 (차원 흐름부터 Keras 구현까지)

> 날짜: 2026-08-24
> 원본 노션: [링크](https://app.notion.com/p/AI-CNN-Keras-3c31d46c18fc803f991fcfb13dc08a19)

---

### 딥러닝 계층별 데이터 차원(Shape)의 흐름과 변화

> 한 줄 요약: 입체 이미지 (Height, Width, Channel)를 Conv2D와 MaxPooling으로 특징을 뽑아 크기를 줄이고, Flatten으로 1차원으로 길게 편 뒤, Dense를 거쳐 최종 정답 개수만큼의 1차원 벡터로 압축해 내보냅니다.

- MNIST 기준 실제 차원 변화 흐름 (28 \times 28 흑백 이미지 예시):
- 층별 핵심 변경 규칙:
### 손실 함수 선택 표준 가이드

- 수치(연속값) 예측 (회귀): MSE 또는 MAE
- 2개 중 택1 (이진 분류): binary_crossentropy
- 3개 이상 중 택1 (다중 분류): categorical_crossentropy (원핫 인코딩) / sparse_categorical_crossentropy (정수 라벨)
### 핵심 레이어 및 활성화 함수 비교 (Conv2D vs Sigmoid vs Softmax)

| 구분 | 합성곱 (Conv2D) | 시그모이드 (Sigmoid) | 소프트맥스 (Softmax) |
|---|---|---|---|
| 핵심 역할 | 이미지 특징 추출 (눈) | 이진 분류 판정 (Yes/No) | 다중 분류 판정 (N개 중 택1) |
| 배치 위치 | 신경망의 앞단 (특징 추출 영역) | 출력층 맨 끝 (Dense(1)) | 출력층 맨 끝 (Dense(N)) |
| 수행 작업 | 3 \times 3 필터로 윤곽선, 질감 등 공간 패턴 스캔 | 임의의 실수 점수를 0.0 \sim 1.0 단일 확률로 변환 | N개 점수를 합이 1.0(100%)이 되는 N개 확률로 변환 |
| 출력 형태 | Feature Map (3차원 텐서) | 숫자 1개 (예: 0.85) | 숫자 N개 배열 (예: [0.1, 0.7, 0.2]) |
| 대표 예시 | 고양이의 귀 모양, 자동차 바퀴 윤곽 감지 | 스팸 메일 여부, 고혈압 판정 | 손글씨 숫자(0~9), 동물 품종 분류 |

한 줄 요약

- Conv2D: "이미지에서 중요한 시각적 특징들을 찾아낸다."
- Sigmoid: "찾아낸 특징을 보고 '이게 맞을 확률(0~100%)' 1개를 구한다."
- Softmax: "찾아낸 특징을 보고 'A, B, C 후보 각각일 확률의 합을 100%'로 나눠 담는다."


## 합성곱 신경망 (Convolutional Neural Network, CNN)

”2차원 격자 구조를 가진 데이터(주로 이미지)가 들어왔을 때, 공간 정보를 유지한 채 특징 추출(Conv2D + ReLU)과 압축(MaxPooling2D)을 반복하고, 이를 1차원으로 펴서(Flatten) 최종 목표(분류/회귀)에 맞게 점수를 계산해 출력하는 신경망”

왜 기존 다층 퍼셉트론(MLP) 대신 CNN을 쓸까?

- MLP의 치명적 한계 (Flatten의 문제점):
- CNN의 해결 방식:
CNN 핵심 3대 구성 요소

- 합성곱 층 (Conv2D - 돋보기로 특징 찾기):
- 활성화 함수 (ReLU - 중요 특징 강조):
- 풀링 층 (MaxPooling2D - 이미지 요약/압축):
CNN 전체 파이프라인 흐름

```plain text
[입력 이미지] ──> [Conv2D + ReLU + MaxPool] ──> [Conv2D + ReLU + MaxPool] ──> [Flatten] ──> [Dense (출력층)]
 (2D 격자 유지) ──> (저수준 특징: 점, 선 추출) ──> (고수준 특징: 눈, 코, 바퀴 추출) ──> (1D로 압축) ──> (최종 분류 판정)
```

- 특징 추출 영역 (Feature Extraction): Conv2D와 MaxPooling을 반복하며 점 \rightarrow 선 \rightarrow 복잡한 물체 형태를 단계적으로 학습
- 분류 영역 (Classification): 추출된 최종 특징들을 Flatten으로 1차원으로 펴준 뒤, 일반 Dense 신경망에 연결해 최종 확률(Softmax/Sigmoid)을 계산
Keras 표준 CNN 모델 코드 템플릿

```python
import tensorflow as tf

model = tf.keras.Sequential([
    # 1. 입력층: 28x28 크기, 1개 채널(흑백) 이미지 지정
    tf.keras.Input(shape=(28, 28, 1)),

    # 2. 첫 번째 특징 추출 블록
    tf.keras.layers.Conv2D(filters=32, kernel_size=(3, 3), padding='same', activation='relu'),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)), # 이미지 크기가 28x28 -> 14x14로 축소

    # 3. 두 번째 특징 추출 블록
    tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), padding='same', activation='relu'),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)), # 이미지 크기가 14x14 -> 7x7로 축소

    # 4. 분류를 위한 Flatten 및 완전연결층(Dense)
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.2),                   # 과적합 방지

    # 5. 최종 출력층: 10개 클래스 다중 분류
    tf.keras.layers.Dense(10, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)
```

