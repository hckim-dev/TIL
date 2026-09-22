# \[AI\] CNN 구조와 파이프라인 완벽 정리 (차원 흐름부터 Keras 구현까지)

> 날짜: 2026-08-24
> 원본 노션: [링크](https://app.notion.com/p/AI-CNN-Keras-3c31d46c18fc803f991fcfb13dc08a19)

<!-- notion-page-id: 3c31d46c18fc803f991fcfb13dc08a19 -->
<!-- notion-title: "[AI] CNN 구조와 파이프라인 완벽 정리 (차원 흐름부터 Keras 구현까지)" -->

---

<a id="notion-3c61d46c18fc80daa589c52cf8633a88"></a>

### 딥러닝 계층별 데이터 차원(Shape)의 흐름과 변화

> **한 줄 요약:** 입체 이미지 `(Height, Width, Channel)`를 `Conv2D`와 `MaxPooling`으로 특징을 뽑아 크기를 줄이고, `Flatten`으로 1차원으로 길게 편 뒤, `Dense`를 거쳐 최종 **정답 개수만큼의 1차원 벡터**로 압축해 내보냅니다.

- <strong>MNIST 기준 실제 차원 변화 흐름 (</strong><strong>$28 \times 28$</strong> <strong>흑백 이미지 예시):</strong>

  ```text
  [입력 이미지] (28, 28, 1)
        ↓ Conv2D (필터 32개, padding='same')
  [특징 맵]     (28, 28, 32)   ← 가로/세로 유지, 채널만 32개로 확장
        ↓ MaxPooling2D ((2,2))
  [크기 압축]   (14, 14, 32)   ← 가로/세로 절반(1/2) 축소
        ↓ Flatten
  [1차원 변환]  (6,272)        ← 14 × 14 × 32 = 6,272개 숫자로 일렬 정렬
        ↓ Dense(10, activation='softmax')
  [최종 출력]   (10,)          ← 0~9 각 클래스별 확률 10개
  ```
- **층별 핵심 변경 규칙:**

  - <strong>`Conv2D`</strong><strong>:</strong> 가로/세로 유지(`same` 기준), **채널 수 = 필터 개수**
  - <strong>`MaxPooling2D`</strong><strong>:</strong> <strong>가로/세로 크기 절반(</strong><strong>$1/2$</strong><strong>)으로 축소</strong>, 채널 수 유지
  - <strong>`Flatten`</strong><strong>:</strong> $H \times W \times C$를 곱해 **1차원 배열로 펼침**
  - <strong>`Dense(N)`</strong><strong>:</strong> 이전 크기와 무관하게 <strong>최종 출력 개수를</strong> <strong>$N$</strong>**개로 압축**

<a id="notion-3c61d46c18fc8058bc3af1fd47173dcb"></a>

### **손실 함수 선택 표준 가이드**

- **수치(연속값) 예측 (회귀):** **`MSE`** 또는 `MAE`

  - 예: 집값, 온도, 주가, 시험 점수 예측
- **2개 중 택1 (이진 분류):** **`binary_crossentropy`**

  - 예: 스팸 메일(0/1), 암 판정(음성/양성)
- **3개 이상 중 택1 (다중 분류):** **`categorical_crossentropy`** (원핫 인코딩) / **`sparse_categorical_crossentropy`** (정수 라벨)

  - 예: MNIST 숫자(0\~9), 붓꽃 품종(0/1/2)

<a id="notion-3c61d46c18fc800cb420f774044f2e64"></a>

### 핵심 레이어 및 활성화 함수 비교 (Conv2D vs Sigmoid vs Softmax)

|  |  |  |  |
| --- | --- | --- | --- |
| **구분** | **합성곱 (Conv2D)** | **시그모이드 (Sigmoid)** | **소프트맥스 (Softmax)** |
| **핵심 역할** | **이미지 특징 추출 (눈)** | **이진 분류 판정 (Yes/No)** | **다중 분류 판정 (N개 중 택1)** |
| **배치 위치** | 신경망의 **앞단 (특징 추출 영역)** | 출력층 <strong>맨 끝 (</strong><strong>`Dense(1)`</strong><strong>)</strong> | 출력층 <strong>맨 끝 (</strong><strong>`Dense(N)`</strong><strong>)</strong> |
| **수행 작업** | $3 \times 3$ 필터로 윤곽선, 질감 등 공간 패턴 스캔 | 임의의 실수 점수를 **$0.0 \sim 1.0$** <strong>단일 확률</strong>로 변환 | $N$개 점수를 <strong>합이</strong> <strong>$1.0(100%)$</strong><strong>이 되는</strong> <strong>$N$</strong>**개 확률**로 변환 |
| **출력 형태** | Feature Map (3차원 텐서) | 숫자 1개 (예: `0.85`) | 숫자 $N$개 배열 (예: `[0.1, 0.7, 0.2]`) |
| **대표 예시** | 고양이의 귀 모양, 자동차 바퀴 윤곽 감지 | 스팸 메일 여부, 고혈압 판정 | 손글씨 숫자(0\~9), 동물 품종 분류 |

**한 줄 요약**

- <strong>`Conv2D`</strong><strong>:</strong> "이미지에서 중요한 시각적 특징들을 찾아낸다."
- <strong>`Sigmoid`</strong><strong>:</strong> "찾아낸 특징을 보고 '이게 맞을 확률(0\~100%)' 1개를 구한다."
- <strong>`Softmax`</strong><strong>:</strong> "찾아낸 특징을 보고 'A, B, C 후보 각각일 확률의 합을 100%'로 나눠 담는다."

<br>

<a id="notion-3c61d46c18fc80df8612cc1806b9c59e"></a>

## 합성곱 신경망 (Convolutional Neural Network, CNN)

”2차원 격자 구조를 가진 데이터(주로 이미지)가 들어왔을 때, 공간 정보를 유지한 채 특징 추출(`Conv2D + ReLU`)과 압축(`MaxPooling2D`)을 반복하고, 이를 1차원으로 펴서(`Flatten`) 최종 목표(분류/회귀)에 맞게 점수를 계산해 출력하는 신경망”

**왜 기존 다층 퍼셉트론(MLP) 대신 CNN을 쓸까?**

- <strong>MLP의 치명적 한계 (</strong><strong>`Flatten`</strong>**의 문제점):**

  - $28 \times 28$ 크기의 강아지 사진을 1차원($784$)으로 길게 펴면, **픽셀 간의 상/하/좌/우 연결 관계(공간 정보)가 완전히 파괴**됩니다.
  - 이미지가 조금만 옆으로 치우치거나 회전해도 다른 사물로 잘못 인식합니다.
- **CNN의 해결 방식:**

  - 이미지를 1차원으로 펴지 않고 **2차원 격자 그대로 돋보기(필터)로 훑으며 특징을 추출**합니다.
  - 위치가 어디에 있든 고유한 윤곽선과 패턴을 유지한 채 찾아낼 수 있습니다.

**CNN 핵심 3대 구성 요소**

- <strong>합성곱 층 (</strong><strong>`Conv2D`</strong> <strong>\- 돋보기로 특징 찾기):</strong>

  - 작은 사각형 틀(필터/커널, 보통 $3 \times 3$)이 이미지를 좌우상하로 스캔하며 연산합니다.
  - 선, 모서리, 동그라미, 질감 같은 시각적 특징 지도(Feature Map)를 생성합니다.
  - **Filters (필터 개수):** 찾아낼 특징의 가짓수 (예: 32개, 64개)
  - **Kernel Size (필터 크기):** 돋보기의 크기 (보통 `(3, 3)`)
  - <strong>Padding (</strong><strong>`'same'`</strong> <strong>/</strong> <strong>`'valid'`</strong><strong>):</strong>

    - `same`: 외곽에 0을 둘러 필터를 거쳐도 원본 이미지 크기 유지
    - `valid`: 패딩 없이 필터를 돌아 크기가 조금 줄어듦
- <strong>활성화 함수 (</strong><strong>`ReLU`</strong> <strong>\- 중요 특징 강조):</strong>

  - 합성곱 연산 결과에서 음수는 0으로 날리고, **강하게 감지된 특징(양수)만 남겨 활성화**합니다.
- <strong>풀링 층 (</strong><strong>`MaxPooling2D`</strong> <strong>\- 이미지 요약/압축):</strong>

  - 일정 영역(예: $2 \times 2$)에서 **가장 큰 특징값(최댓값) 1개만 골라내어 이미지 크기를 절반으로 줄입니다.**
  - 데이터 계산량을 대폭 줄이고, 사물의 위치가 조금 바뀌어도 흔들리지 않는 내성(위치 불변성)을 확보합니다.

**CNN 전체 파이프라인 흐름**

```text
[입력 이미지] ──> [Conv2D + ReLU + MaxPool] ──> [Conv2D + ReLU + MaxPool] ──> [Flatten] ──> [Dense (출력층)]
 (2D 격자 유지) ──> (저수준 특징: 점, 선 추출) ──> (고수준 특징: 눈, 코, 바퀴 추출) ──> (1D로 압축) ──> (최종 분류 판정)
```

- **특징 추출 영역 (Feature Extraction):** `Conv2D`와 `MaxPooling`을 반복하며 점 $\rightarrow$ 선 $\rightarrow$ 복잡한 물체 형태를 단계적으로 학습
- **분류 영역 (Classification):** 추출된 최종 특징들을 `Flatten`으로 1차원으로 펴준 뒤, 일반 `Dense` 신경망에 연결해 <strong>최종 확률(</strong><strong>`Softmax`</strong><strong>/</strong><strong>`Sigmoid`</strong><strong>)을 계산</strong>

**Keras 표준 CNN 모델 코드 템플릿**

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
