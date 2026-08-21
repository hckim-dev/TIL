# [AI] 회귀부터 다중 분류(Softmax), MLP 및 MNIST 실습 정리

> 날짜: 2026-08-21
> 원본 노션: [링크](https://app.notion.com/p/AI-Softmax-MLP-MNIST-3c21d46c18fc809aa114c497e687012b)

---

## 선형 회귀(Linear Regression)

### 1. 환경 준비 및 데이터 불러오기

```python
import numpy as np
import tensorflow as tf
import pandas as pd
import matplotlib.pyplot as plt
```

- 수학 계산(numpy), 딥러닝(tensorflow), 엑셀 표 다루기(pandas), 그래프 그리기(matplotlib) 도구들을 준비합니다.
```python
df = pd.read_csv(files_path)  # CSV 파일(표)을 읽어와 df에 저장
df.head()                     # 데이터가 잘 들어왔나 위에서 5줄만 미리보기
```

### 2. 데이터를 AI가 먹을 수 있는 형태(Tensor)로 가공

```python
x_input = tf.constant(df['X'], dtype=tf.float32)
labels = tf.constant(df['Y'], dtype=tf.float32)

x_input = tf.reshape(x_input, (-1, 1))
labels = tf.reshape(labels, (-1, 1))
```

- tf.constant: 표의 X열(입력 데이터)과 Y열(정답 레이블)을 고정 텐서로 변환합니다.
- tf.reshape(..., (-1, 1)) (중요): 1차원 데이터([1, 2, 3])를 AI 행렬 연산 규격에 맞게 2차원 세로 열 형태([[1], [2], [3]])로 차원을 맞춰줍니다.
```python
# Min-Max 스케일링 (정규화)
x_min, x_max = np.min(x_input, axis=0), np.max(x_input, axis=0)
x_input = (x_input - x_min) / (x_max - x_min)
```

- 데이터 압축: X값이 너무 크면 학습할 때 숫자가 튀어 엉뚱한 곳으로 날아갈 수 있습니다. 모든 X 데이터를 0과 1 사이의 작은 값으로 비율 변환(압축)해 줍니다.
### 3. AI 모델 설계 및 학습

```python
# 1) 모델 조립
model = tf.keras.models.Sequential([
    tf.keras.Input(shape=(1,)),     # 입구: 숫자 1개 들어옴
    tf.keras.layers.Dense(1)        # 퍼셉트론 1대: 결과값 1개 출력 (직선의 식 y = Wx + b)
])

# 2) 채점 기준 및 수정 알고리즘 세팅
model.compile(optimizer='sgd', loss='mse')

# 3) 문제집 1000회독 학습 시작
%%time
history = model.fit(x_input, labels, epochs=1000)
```

- model.compile: 오차는 MSE(평균 제곱 오차)로 계산하고, 틀릴 때마다 경사하강법(SGD)으로 가중치(W, b)를 수정하도록 설정합니다.
- model.fit: 준비된 문제집을 1,000번 반복 학습하며 최적의 W와 b를 찾습니다.
### 4. 학습 상태 확인 (오차 그래프 & 찾아낸 가중치)

```python
# 4. loss 그래프 출력
loss = history.history['loss']
...
plt.semilogy() # 오차가 줄어드는 추세를 한눈에 보기 위해 y축을 로그 스케일로 변환
plt.show()
```

- 1000번 공부하는 동안 오차(Loss)가 0에 가깝게 잘 떨어졌는지 꺾은선 그래프로 확인합니다.
```python
# 5. 가중치 출력
w = model.get_weights()
print(w)
```

- AI가 수없이 문제를 풀며 최종적으로 완성한 직선의 공식 W(기울기)와 B(절편) 값을 확인합니다.
### 5. 테스트 및 새로운 값 예측 (실전 추론)

```python
# 6. 기존 데이터에 대한 예측값 확인
H_x = model.predict(x_input)
for x, h, l in zip(x_input, H_x, labels):
    print("x:{}, h:{}, l:{}".format(x, h, l))
```

- 원래 문제집 데이터(x)를 넣었을 때 AI가 예측한 값(h)이 실제 정답(l)과 얼마나 비슷한지 눈으로 대조합니다.
```python
# 7. X가 115.5일 때 예측
def predict(x):
    # 학습할 때 X를 0~1로 압축했으므로, 새로운 X도 똑같은 비율로 압축해서 입력해야 함!
    return model.predict((x - x_min) / (x_max - x_min))

X = tf.constant([[115.5]], dtype=tf.float32)
print("X: {} -> Y: {:>7.4}".format(X[0,0], predict(X)[0,0]))
```

- 실전 테스트: 한 번도 본 적 없는 새로운 값 115.5가 들어왔을 때, 정규화 공식에 맞춰 변환 후 AI에게 물어보고 예측된 Y값을 출력합니다.
### 6. 정답 vs 예측선 시각화 비교

```python
# 8. 정답선과 AI가 찾은 예측선 비교 그래프
plt.plot(..., label='labels')   # 실제 정답 데이터 라인
plt.plot(..., label='predict')  # AI가 그어낸 최적의 예측 직선
plt.show()
```

- 실제 정답 데이터(labels) 위에 AI가 학습해서 찾아낸 직선(predict)이 얼마나 딱 들어맞게 겹치는지 시각적으로 확인하며 마무리합니다.
## 로지스틱 회귀(Logistic Regression)

### 1. 데이터 준비 및 2차원 정규화

```python
# 나이(Age)와 체질량지수(BMI) 데이터 (입력 특성 2개)
x_input = tf.constant([[25,22], [25,26], ...], dtype=tf.float32)

# 고혈압 여부: 정상(0) 또는 고혈압(1)
labels = tf.constant([[0], [0], [1], ...], dtype=tf.float32)

# Min-Max Scaling (정규화)
x_min, x_max = np.min(x_input, axis=0), np.max(x_input, axis=0)
x_input = (x_input - x_min) / (x_max - x_min)
```

- 입력값 형태: 데이터가 [나이, BMI] 2개 묶음으로 들어오므로 shape=(18, 22) 형태를 갖습니다.
- axis=0 정규화: 나이 열은 나이의 최솟값/최댓값으로, BMI 열은 BMI의 최솟값/최댓값으로 각각 열별(세로축 기준)로 0~1 사이로 압축합니다.
### 2. 모델 구조 설계 (선형 회귀와의 결정적 차이점)

```python
model = tf.keras.models.Sequential([
    tf.keras.Input(shape=(2,)),                     # 🚪 1. 입구: 데이터 2개(나이, BMI)가 들어옴
    tf.keras.layers.Dense(1, activation='sigmoid')  # 🧠 2. 시그모이드 함수 적용!
])
```

- Input(shape=(2,)): 한 번에 2개의 특성(x_1: 나이, x_2: BMI)을 받는 문을 엽니다.
- activation='sigmoid': 계산된 점수를 0과 1 사이의 '확률'로 변환해 주는 S자 곡선(시그모이드) 필터를 적용합니다. (출력값이 0.8이면 "고혈압일 확률 80%"를 의미)
### 3. 컴파일 및 학습 (분류 전용 설정)

```python
model.compile(
    optimizer=tf.keras.optimizers.SGD(learning_rate=0.1),
    loss='binary_crossentropy',   # 🎯 이진 분류 전용 채점 기준 (로그 손실)
    metrics=['accuracy']          # 📊 정확도(몇 %나 맞혔는가)를 함께 기록
)

history = model.fit(x_input, labels, epochs=1000)
```

- loss='binary_crossentropy': Yes/No(0 또는 1)를 맞히는 문제에 최적화된 오차 계산 공식입니다.
- metrics=['accuracy']: 손실(Loss)뿐만 아니라 모델이 18명 중 몇 명을 정확히 맞혔는지 정확도(Accuracy)를 같이 추적합니다.
### 4. 정확도 & 오차 그래프 시각화

```python
loss = history.history['loss']
epochs = range(1, len(loss)+1)

plt.figure(figsize=(6, 10)) # 도화지 크기 설정 (가로 6인치, 세로 10인치)

plt.subplot(2, 1, 1) # 상단: 에폭이 지날수록 정확도(Accuracy)가 100%(1.0)에 가까워지는지 확인, (행 개수, 열 개수, 현재 그릴 위치 번호)
plt.title('Accuracy')
plt.plot(epochs, history.history['accuracy'], 'b', label='train_accuracy')
plt.grid(True) # 격자 눈금 표시
plt.ylabel('Accuracy')
plt.legend(loc='best') # 범례 자동 배치(loc='best' 가장 덜 가리는 최적의 빈 공간 배치)

plt.subplot(2, 1, 2) # 하단: 에폭이 지날수록 손실(Loss)이 0에 가깝게 떨어지는지 확인
plt.title('Loss')
plt.plot(epochs, history.history['loss'], 'b', label='train_loss')
plt.grid(True)
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='best')

plt.show()
```

- 위아래 2칸으로 그래프를 나누어 모델이 제대로 학습되고 있는지 성능 지표를 검증합니다.
### 5. 결과 해석 및 새로운 환자 예측

```python
# 1) 전체 데이터의 예측 확률 확인
H_x = model.predict(x_input)
for x, h, l in zip(x_input_org, H_x, labels):
    print("Age:{}, BMI:{:>7.4} => Result:{:>7.4} [label => {}]".format(x[0], x[1], h[0], l))
```

- Result로 나오는 0~1 사이의 확률값(예: 0.8521)을 실제 정답 라벨 0 또는 1과 비교합니다. (보통 0.5 이상이면 1로 판정)
```python
# 2) 새로운 환자 예측 (나이 50세, BMI 25)
def predict(x):
    return model.predict((x - x_min) / (x_max - x_min))

x_test = tf.constant([[50.0, 25.0]], dtype=tf.float32)
H_x = predict(x_test)

# >: 오른쪽 정렬, 7: 최소 7칸 확보, .4: 실수 4자리로 제한
print("Age : {}, BMI : {} = > RES : {:>7.4}".format(x_test[0,0],x_test[0,1],H_x[0,0]))
```

- 학습 때와 동일하게 0~1로 스케일링한 후 AI에게 질문하여 "50세, BMI 25인 사람이 고혈압일 확률"을 최종 예측값으로 받아냅니다.
## 소프트맥스 분류 (Softmax Classification / 다중 분류)

3개 이상의 선택지(클래스) 중 가장 정답일 확률이 높은 1개를 고르는 다중 클래스 분류(Multi-Class Classification) 알고리즘입니다.

1. 핵심 개념 및 원리

- 시그모이드(Sigmoid)의 확장판:
- 확률 변환 (0 \sim 1 및 총합 1.0):
- 최종 선택 (argmax):
2. 3대 회귀/분류 모델 한눈에 비교

| 구분 | 선형 회귀 (Linear) | 로지스틱 회귀 (Logistic) | 소프트맥스 회귀 (Softmax) |
|---|---|---|---|
| 문제 유형 | 연속 수치 예측 (회귀) | 2개 중 택1 (이진 분류) | 3개 이상 중 택1 (다중 분류) |
| 출력 노드 수 | Dense(1) | Dense(1) | Dense(클래스 개수) (예: 3개면 3) |
| 활성화 함수 | 없음 (직선 y=wx+b) | activation='sigmoid' | activation='softmax' |
| 손실 함수 (Loss) | mse | binary_crossentropy | categorical_crossentropy |
| 대표 예시 | 시험 점수, 집값 예측 | 합격/불합격, 스팸 메일 판정 | 붓꽃(Iris) 품종 분류, 손글씨 숫자(0~9) 인식 |

3. 원-핫 인코딩 (One-Hot Encoding)

다중 분류에서 정답(Label) 데이터를 컴퓨터가 계산하기 편하도록 변환하는 방식입니다.

- 원리: 정답 번호 위치만 1로 켜고 나머지는 모두 0으로 채운 벡터로 변환
> Loss 함수 선택 팁:

4. Keras 핵심 코드 템플릿 (3개 클래스 분류 예시)

```python
import tensorflow as tf

# 1. 모델 정의 (출력 노드 개수 = 클래스 개수 3개, activation = softmax)
model = tf.keras.Sequential([
    tf.keras.Input(shape=(4,)),                      # 입력 특성 4개 (예: 꽃잎/꽃받침 길이·너비)
    tf.keras.layers.Dense(3, activation='softmax')   # 출력 3개 (각 품종일 확률의 합 = 1.0)
])

# 2. 모델 컴파일
model.compile(
    optimizer=tf.keras.optimizers.SGD(learning_rate=0.1),
    loss='categorical_crossentropy',                 # 다중 분류 전용 손실 함수
    metrics=['accuracy']
)

# 3. 예측 및 가장 높은 확률의 클래스 추출
predictions = model.predict(x_test)                  # 예: [[0.1, 0.7, 0.2]]
predicted_class = tf.argmax(predictions, axis=1)    # 1번 클래스 선택
```

### 5. [실습] Softmax 다중 분류 실전 파이프라인

나이(Age)와 체질량지수(BMI) 2가지 정보를 바탕으로 건강 상태를 3가지 범주(0: 정상, 1: 주의, 2: 경고) 중 하나로 분류하는 전체 실습 코드 분석입니다.

1. 데이터 준비 및 원-핫 인코딩 (One-Hot Encoding)

```python
# 1) 입력 데이터: [나이, BMI] (18명, 특성 2개 -> shape=(18, 2))
x_input = tf.constant([[25,22], [25,26], ...], dtype=tf.float32)

# 2) 정답 레이블: 3개 클래스 원-핫 벡터 (shape=(18, 3))
# 0번(정상): [1,0,0] / 1번(주의): [0,1,0] / 2번(경고): [0,0,1]
labels = tf.constant([[1,0,0], [0,1,0], [0,0,1], ...], dtype=tf.float32)

# 3) Min-Max 정규화: 열별(axis=0)로 나이와 BMI를 각각 0~1로 압축
x_min, x_max = np.min(x_input, axis=0), np.max(x_input, axis=0)
x_input = (x_input - x_min) / (x_max - x_min)
```

2. 모델 아키텍처 및 학습 설정 (다중 분류 세팅)

```python
# 1) 모델 구조: 3개의 클래스별 확률을 출력하도록 설정
model = tf.keras.models.Sequential([
    tf.keras.Input(shape=(2,)),                     # 입구: 나이, BMI (2개)
    tf.keras.layers.Dense(3, activation='softmax')  # 출구: 3개 클래스 확률 (합=1.0)
])

# 2) 컴파일: 다중 분류 전용 손실 함수 지정
model.compile(
    optimizer=tf.keras.optimizers.SGD(learning_rate=0.1),
    loss='categorical_crossentropy',                # 원-핫 레이블 전용 Cross-Entropy
    metrics=['accuracy']                            # 정확도(%) 추적
)

# 3) 모델 학습
history = model.fit(x_input, labels, epochs=1000)
```

3. 학습 곡선 시각화 (정확도 & 손실)

```python
# 2행 1열 서브플롯으로 상단은 정확도(Accuracy), 하단은 오차(Loss) 출력
plt.subplot(2, 1, 1)  # 에폭이 늘어날수록 정확도가 1.0(100%)에 가까워지는지 확인
plt.subplot(2, 1, 2)  # 에폭이 늘어날수록 손실이 0에 가깝게 떨어지는지 확인
```

4. 결과 해석 및 np.argmax() 활용 추론

```python
# 1) 기존 데이터 결과 대조
H_x = model.predict(x_input)
for x, h, l in zip(x_input_org, H_x, labels):
    # np.argmax(): [0.1, 0.7, 0.2] 중 가장 큰 값의 위치 인덱스(1)를 반환
    print("Age:{},BMI:{} [label:{}]=>class:{}: {}".format(
        x[0], x[1], np.argmax(l), np.argmax(h), h
    ))

# 2) 신규 환자 예측 (나이 50세, BMI 25)
x_test = tf.constant([[50.0, 25.0]], dtype=tf.float32)
H_x = predict(x_test)  # 출력 예: [0.08, 0.79, 0.13] (정상 8%, 주의 79%, 경고 13%)

# np.argmax(H_x[0])을 통해 가장 확률이 높은 1번(주의) 클래스를 최종 판정으로 추출
print("Age : {}, BMI : {} => Class: {}".format(
    x_test[0,0], x_test[0,1], np.argmax(H_x[0])), H_x[0]
)
```

## 다층 퍼셉트론 (Multi-Layer Perceptron, MLP)

입력층과 출력층 사이에 1개 이상의 은닉층(Hidden Layer)을 두어, 단층 퍼셉트론으로는 해결할 수 없는 비선형 문제(예: XOR 문제)를 해결하는 가장 기본적인 인공신경망(ANN) 구조입니다.

1. 단층 퍼셉트론의 한계와 은닉층의 필요성

- 단층 퍼셉트론 (Single-Layer): 입력 \rightarrow 출력 사이에 층이 없어 오직 1개의 직선(Linear)만 그을 수 있음 \rightarrow 직선 1개로는 나눌 수 없는 XOR 문제 해결 불가
- 다층 퍼셉트론 (Multi-Layer): 중간에 은닉층(Hidden Layer)과 비선형 활성화 함수(예: ReLU)를 추가하여 공간을 비틀고 쪼갬 \rightarrow 복잡한 곡선 형태의 경계선 생성 가능
2. MLP의 3단계 계층 구조

```plain text
[입력층 (Input Layer)] ──> [은닉층 (Hidden Layers)] ──> [출력층 (Output Layer)]
  (데이터 특성 수용)       (특징 추출 및 비선형 변환)      (최종 예측/분류 결과)
```

- 입력층 (Input Layer): 가공되지 않은 데이터(Feature)가 들어오는 관문 (연산 없음)
- 은닉층 (Hidden Layer):
- 출력층 (Output Layer): 문제 유형에 맞춰 최종 결과 도출
3. 비선형 활성화 함수 (Activation Function)

은닉층에 활성화 함수가 없으면 아무리 층을 깊게 쌓아도 결국 하나의 큰 선형 연산(W_2(W_1x + b_1) + b_2 = W'x + b')으로 합쳐져 단층 구조와 똑같아집니다.

- ReLU (Rectified Linear Unit): 은닉층에서 가장 기본적이고 널리 쓰이는 표준 활성화 함수 (f(x) = \max(0, x))
4. Keras 구현 템플릿 (XOR / 다층 구조 예시)

```python
import tensorflow as tf

# 은닉층이 포함된 다층 퍼셉트론 모델 구성
model = tf.keras.Sequential([
    # 1. 입력층: 특성 2개 수용
    tf.keras.Input(shape=(2,)),

    # 2. 은닉층 1: 노드 8개 + 비선형 변환(ReLU)
    tf.keras.layers.Dense(8, activation='relu'),

    # 3. 은닉층 2: 노드 4개 + 비선형 변환(ReLU)
    tf.keras.layers.Dense(4, activation='relu'),

    # 4. 출력층: 이진 분류용 시그모이드 (0 또는 1 예측)
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
    loss='binary_crossentropy',
    metrics=['accuracy']
)
```

## MNIST 손글씨 숫자 분류 (다층 퍼셉트론 실전)

MNIST는 0부터 9까지 손으로 쓴 28 \times 28 픽셀 크기의 흑백 숫자 이미지 데이터셋으로, 딥러닝 분야의 'Hello World'에 해당하는 대표적인 다중 클래스 분류 문제입니다.

1. 데이터셋 구조 및 핵심 전처리

- 데이터 규격:
- 정규화 (Normalization):
- 평탄화 (Flatten):
2. 전체 실전 코드 파이프라인

```python
import tensorflow as tf
import matplotlib.pyplot as plt

# 1. 데이터 로드 및 정규화 (0~255 -> 0.0~1.0)
mnist = tf.keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

# 2. MLP 모델 아키텍처 설계
model = tf.keras.Sequential([
    # 2차원(28, 28) 입력을 1차원(784)으로 펴주는 Flatten 레이어
    tf.keras.Input(shape=(28, 28)),
    tf.keras.layers.Flatten(),

    # 은닉층: 128개 노드 + ReLU 활성화 함수
    tf.keras.layers.Dense(128, activation='relu'),

    # 과적합 방지를 위해 학습 중 임의로 20% 뉴런을 끔
    tf.keras.layers.Dropout(0.2),

    # 출력층: 10개 숫자(0~9) 각각에 대한 확률 출력 (합 = 1.0)
    tf.keras.layers.Dense(10, activation='softmax')
])

# 3. 모델 컴파일
model.compile(
    optimizer='adam',
    # 정답 레이블이 원-핫 벡터([0,0,1...])가 아닌 일반 정수(0~9)일 때 사용하는 손실 함수
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# 4. 모델 학습
history = model.fit(x_train, y_train, epochs=5, batch_size=64, validation_split=0.1)

# 5. 테스트 데이터로 최종 성능 평가
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print(f"테스트 정확도: {test_acc * 100:.2f}%")

# 6. 실전 예측 및 결과 확인 (테스트 1번 이미지)
predictions = model.predict(x_test[:1])
predicted_number = tf.argmax(predictions[0]).numpy()
print(f"AI 예측값: {predicted_number}, 실제 정답: {y_test[0]}")
```

3. 주요 구성 요소 핵심 정리

- tf.keras.layers.Flatten(): 28 \times 28 행렬 데이터를 순서대로 한 줄로 길게 늘어뜨려 784개의 1차원 벡터로 변환
- tf.keras.layers.Dropout(0.2): 학습 시 뉴런의 20%를 무작위로 쉬게 만들어 특정 뉴런에만 과도하게 의존하는 과적합(Overfitting)을 방지
- sparse_categorical_crossentropy: 정답 데이터(y_train)를 to_categorical()로 원-핫 인코딩하지 않고, 0, 1, 2... 같은 기본 정수 형태 그대로 손실을 계산할 때 사용
