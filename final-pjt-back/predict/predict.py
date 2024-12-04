
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from tensorflow.keras import backend as K
from keras.callbacks import EarlyStopping 
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import datetime
from datetime import timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import r2_score

#모델 성능 테스트
# 1. 데이터 다운로드
def get_stock_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data[['Close']], data.index  # 종가만 사용

ticker = '005930.KS'  # 삼성전자 (KRX 종목은 .KS를 붙임)
start_date = '2021-01-01'
today = datetime.date.today()
yesterday = today - timedelta(days=1)
end_date = yesterday

stock_data, dates= get_stock_data(ticker, start_date, end_date)

today_close = stock_data.iloc[-1]['Close']  # stock_data는 원래 종가 데이터
split_date=today - timedelta(days=365) #1년치 데이터로 테스트
train_data=pd.DataFrame(stock_data.loc[:split_date, ['Close']])
test_data=pd.DataFrame(stock_data.loc[split_date:, ['Close']])


# 2. 데이터 전처리
scaler = MinMaxScaler()#정규화
train_data_sc = scaler.fit_transform(train_data)
test_data_sc = scaler.transform(test_data)


train_sc_df=pd.DataFrame(train_data_sc, columns=['Scaled'], index=train_data.index)
test_sc_df=pd.DataFrame(test_data_sc, columns=['Scaled'], index=test_data.index)

#지연 데이터 생성
for i in range(1, 31):
    train_sc_df ['Scaled_{}'.format(i)]=train_sc_df ['Scaled'].shift(i)
    test_sc_df ['Scaled_{}'.format(i)]=test_sc_df ['Scaled'].shift(i)


#nan 제거
x_train=train_sc_df.dropna().drop('Scaled', axis=1)
y_train=train_sc_df.dropna()[['Scaled']]

x_test=test_sc_df.dropna().drop('Scaled', axis=1)
y_test=test_sc_df.dropna()[['Scaled']]

x_train=x_train.values
x_test=x_test.values

y_train=y_train.values
y_text=y_test.values


# 입력 데이터를 LSTM 입력 형식으로 변환
x_train_t = x_train.reshape(x_train.shape[0], 30, 1)
x_test_t = x_test.reshape(x_test.shape[0], 30, 1)
print(x_test_t)
print(np.isnan(x_test_t).any())  # NaN 값이 있는지 확인
print(np.isinf(x_test_t).any())  # Inf 값이 있는지 확인

#예측 모델 생성
K.clear_session()
model = Sequential()
model.add(LSTM(64, return_sequences=True, input_shape=(30, 1)))
model.add(LSTM(64, return_sequences=True))
model.add(LSTM(64, return_sequences=False))
model.add(Dense(1, activation='linear'))  # 90일 예측
model.compile(optimizer='adam', loss='mean_squared_error')

#예측 모델 학습
early_stopping = EarlyStopping(monitor='loss', patience=5, verbose=1)
model.fit(x_train_t, y_train, epochs=50, batch_size=32, callbacks=[early_stopping])
#epochs: 훈련 반복 사이즈, batch_size:한번에 입력되는 데이터의 크기

# 예측
predicted = model.predict(x_test_t)
predicted_original = scaler.inverse_transform(predicted)
y_test_original = scaler.inverse_transform(y_test)
t_df=test_sc_df.dropna()
y_test_df=pd.DataFrame(y_test_original, columns=['Close'], index=t_df.index)
y_pred_df=pd.DataFrame(predicted_original, columns=['Close'], index=t_df.index)

#예측 모델의 신뢰도
#MSE: 예측 값과 실제 값의 차이를 제곱한 값의 평균
#MAE: 예측 값과 실제 값의 차이의 절대값 평균
rmse = np.sqrt(mean_squared_error(y_test_original, predicted_original))
mae = mean_absolute_error(y_test_original, predicted_original)
r2 = r2_score(y_test_original, predicted_original)
print(f"결정계수 R²: {r2*100}%")#1에 가까울수록 신뢰도가 높다.
print(f"RMSE: {rmse:.2f}, MAE: {mae:.2f}")#값이 작을수록 신뢰도가 높다

ax1=y_test_df.plot()
y_pred_df.plot(ax=ax1)
plt.legend(['test','pred'])
plt.xticks(rotation=45)
plt.show()

#성능 검증 후 최근 데이터 추가 학습
additional_data, additional_dates = get_stock_data(ticker, split_date, yesterday)

# 기존 train_data와 추가 데이터를 합침
new_train_data = pd.concat([train_data, additional_data])

# 정규화 (scaler를 사용해 기존 정규화 범위를 유지)
new_train_data_sc = scaler.fit_transform(new_train_data)

# 새로운 데이터프레임 생성
new_train_sc_df = pd.DataFrame(new_train_data_sc, columns=['Scaled'], index=new_train_data.index)

# 지연 데이터 생성 (새로운 학습 데이터를 위해)
for i in range(1, 31):
    new_train_sc_df['Scaled_{}'.format(i)] = new_train_sc_df['Scaled'].shift(i)

# NaN 제거
x_new_train = new_train_sc_df.dropna().drop('Scaled', axis=1).values
y_new_train = new_train_sc_df.dropna()[['Scaled']].values

# LSTM 입력 형식으로 변환
x_new_train_t = x_new_train.reshape(x_new_train.shape[0], 30, 1)
# 기존 모델에 추가 학습 (Fine-Tuning)
model.fit(x_new_train_t, y_new_train, epochs=20, batch_size=32, verbose=1)



def predict_next_n_days(model, last_30_days, scaler, n_days=90):
 
    predictions = []
    input_data = last_30_days.copy()

    for _ in range(n_days):
        pred = model.predict(input_data)
        predictions.append(pred[0, 0])

        # 입력 데이터 업데이트
        pred_reshaped = pred.reshape(1, 1, 1)  # (1, 1, 1)로 차원 확장
        input_data = np.append(input_data[:, 1:, :], pred_reshaped, axis=1)

    # 스케일 복원
    predictions_original = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
    return predictions_original

# 마지막 30일 데이터를 준비하고, 90일간 예측
# 마지막 30일 데이터 업데이트
new_last_30_days = new_train_sc_df.drop('Scaled', axis=1).iloc[-1:].values.reshape(1, 30, 1)

# 90일 예측
new_future_90_days = predict_next_n_days(model, new_last_30_days, scaler, n_days=90)

# 새로운 예측 결과 시각화
new_future_dates = [new_train_data.index[-1] + timedelta(days=i + 1) for i in range(90)]
new_predicted_df = pd.DataFrame({'Date': new_future_dates, 'Predicted Close': new_future_90_days.flatten()})
new_predicted_df.set_index('Date', inplace=True)

plt.figure(figsize=(12, 6))
plt.plot(new_predicted_df.index, new_predicted_df['Predicted Close'], label='Updated Predicted Prices', marker='o')
plt.title('Updated Next 90 Days Predicted Closing Prices', fontsize=16)
plt.xlabel('Date', fontsize=14)
plt.ylabel('Price', fontsize=14)
plt.legend()
plt.grid()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

plt.savefig('predicted_prices.png')
plt.close()
graph_data = new_predicted_df.reset_index().to_dict(orient='records')
data={
    'graph_data':graph_data,
    'r2': r2*100
}
print(data)