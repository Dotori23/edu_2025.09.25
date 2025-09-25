

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os


# 한글 폰트 설정 (NanumGothic_Regular.ttf)
font_path = os.path.join(os.path.dirname(__file__), '../fonts/NanumGothic-Regular.ttf')
if os.path.exists(font_path):
	fm.fontManager.addfont(font_path)
	plt.rc('font', family='NanumGothic')
	plt.rcParams['axes.unicode_minus'] = False

st.title('불연속 함수의 불연속점 시각화')

# 임의의 불연속 함수 예시 (사용자가 선택 가능)
# 함수 정의 및 불연속점 이론값(참고용)
def sign_func(x):
	return np.sign(x)
def inv_func(x):
	return 1/x
def floor_func(x):
	return np.floor(x)
def heaviside_func(x):
	return np.heaviside(x, 0.5)

func_options = {
	'sign(x)': sign_func,
	'1/x': inv_func,
	'floor(x)': floor_func,
	'Heaviside(x)': heaviside_func,
}

func_name = st.selectbox('함수를 선택하세요', list(func_options.keys()))
func = func_options[func_name]

# x 범위 설정
x_min = st.number_input('x 최소값', value=-5.0)
x_max = st.number_input('x 최대값', value=5.0)
num_points = st.slider('샘플 포인트 수', min_value=100, max_value=2000, value=500)

x = np.linspace(x_min, x_max, num_points)

# 함수값 계산 (예외 처리)
with np.errstate(divide='ignore', invalid='ignore'):
	y = func(x)

# 불연속점 탐지 개선: 인접한 값 차이가 큰 곳, 무한대/NaN, 함수별 특성 반영
discont_x = []
threshold = 1.5  # 점프 크기 기준 (함수별로 다를 수 있음)
for i in range(1, len(y)):
	# 무한대/NaN
	if not np.isfinite(y[i]) or not np.isfinite(y[i-1]):
		discont_x.append(x[i])
	# sign(x): x=0에서 점프
	elif func_name == 'sign(x)' and x[i-1] < 0 < x[i]:
		discont_x.append(0.0)
	# 1/x: x=0에서 무한대로 점프
	elif func_name == '1/x' and x[i-1] < 0 < x[i]:
		discont_x.append(0.0)
	# floor(x): x가 정수 지날 때마다 점프
	elif func_name == 'floor(x)':
		if int(x[i-1]) != int(x[i]):
			discont_x.append(np.round(x[i], 6))
	# Heaviside(x): x=0에서 점프
	elif func_name == 'Heaviside(x)' and x[i-1] < 0 < x[i]:
		discont_x.append(0.0)
	# 일반 jump
	elif np.abs(y[i] - y[i-1]) > threshold:
		discont_x.append(np.round(x[i], 6))

# 중복 제거 및 정렬
discont_x = sorted(set([float(np.round(val, 6)) for val in discont_x]))

# 그래프 그리기
fig, ax = plt.subplots()
ax.plot(x, y, label=func_name)
if len(discont_x) > 0:
	ax.scatter(discont_x, func(np.array(discont_x)), color='red', label='불연속점', zorder=5)
ax.legend()
ax.set_xlabel('x')
ax.set_ylabel('f(x)')
ax.set_title(f'{func_name}의 그래프와 불연속점')
st.pyplot(fig)

if len(discont_x) > 0:
	st.write(f"불연속점 x좌표: {discont_x}")
else:
	st.write("불연속점이 탐지되지 않았습니다.")
