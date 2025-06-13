import requests
import pandas as pd
from binstar_client.pprintb import user_list
from tqdm import tqdm
import json
import os

if not os.path.exists('data'):
    os.makedirs('data/id')
    os.makedirs('data/env')
    os.makedirs('data/season')
    os.makedirs('data/cultivate')

def check_farm_id(serviceKey, itemcode):
    # 농가 지역, 코드, 작목 확인 API 주소
    id_url = f'http://www.smartfarmkorea.net/Agree_WS/webservices/ProvideRestService/getIdentityDataList/{serviceKey}'

    # 데이터 확인
    response = requests.get(id_url)
    if response.status_code == 200:
        data = response.json()
        # print(data)
    else:
        print(f"Error: {response.status_code} - {response.text}")

    json_data = response.json()

    # JSON 데이터를 DataFrame으로 변환 후 csv 저장
    id_csv = pd.DataFrame.from_dict(json_data)

    tomato_csv = id_csv[id_csv['itemCode'] == f'{itemcode}']

    print(tomato_csv.head())
    tomato_csv.to_csv(f'data/id/{itemcode}_data.csv', index=False, encoding='utf-8-sig')

def check_farm_id_real(serviceKey, itemcode):
    years = list(range(2015, 2026))
    df_list = []
    for year in years:
        url = f'http://www.smartfarmkorea.net/Agree_WS/webservices/CropseasonRestService/getCroppingSeasonDataList/{serviceKey}/{year}'

        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data)
        print(df.head())
        df_list.append(df)

    # 모든 연도의 데이터 합치기
    all_data = pd.concat(df_list, ignore_index=True)

    # 특정 작목, 환경정보, 생육정보가 있는 데이터 추출
    tomato_data = all_data[
        (all_data['itemCode'] == f'{itemcode}') & (all_data['acqAutoYn'] == 'Y') & (all_data['acqCultiYn'] == 'Y')]
    tomato_data.to_csv(f'data/id/{itemcode}_cropping_data.csv', index=False, encoding='utf-8-sig')


def check_farm_season(serviceKey, user_list, itemcode):
    # 작목별 농가 작기정보 조회 API 주소 (사용자별 작기 일자 추출)
    user_season = {}
    # 데이터 없는 농가 수
    error_count = 0

    for user in tqdm(user_list):
        try:
            season_url = f"http://www.smartfarmkorea.net/Agree_WS/webservices/ProvideRestService/getCroppingSeasonDataList/{serviceKey}/{user}"
            response_s = requests.get(season_url)
            data = response_s.json()
            start_date = data[0]['croppingDate']
            end_date = data[0]['croppingEndDate']

            # 날짜 범위 생성
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')

            # 문자열 리스트로 변환
            date_list = date_range.strftime('%Y-%m-%d').tolist()

            # 농가별 날짜(작기) 리스트 저장
            user_season[user] = date_list

        except ValueError as e:
            print(f"ValueError: {e}")
            error_count += 1

    # 작기 정보 json 저장
    with open(f'data/season/{itemcode}_season_data_y.json', 'w', encoding='utf-8') as f:
        json.dump(user_season, f, ensure_ascii=False, indent=2)

    # 데이터 없는 농가 수 출력
    print(error_count)


def check_farm_env(serviceKey, season_data, sect, fatr, itemcode):
    data_list = []

    for i, x in tqdm(season_data.items()):
        for j in x:
            # 시설 id
            facilityId = i + "_01"
            # 측정일자 (season_data.json에 저장된 날짜)
            measDate = j
            # 분야코드(시설원예=FG)
            fldCode = "FG"
            # 분류코드(내부환경=EI)
            sectCode = sect
            # 항목코드(내부온도=TI)
            fatrCode = fatr
            # 작물코드(토마토=80300)
            itemCode = itemcode

            try:
                env_url = f'http://www.smartfarmkorea.net/Agree_WS/webservices/ProvideRestService/getEnvDataList/{serviceKey}/{facilityId}/{measDate}/{fldCode}/{sectCode}/{fatrCode}/{itemCode}'

                result = requests.get(env_url).json()
                data_list.append(result[0])

            except Exception as e:
                print(f"Error fetching data for {facilityId} on {measDate}: {e}")
            except KeyError as e:
                print(f"KeyError: {e} for {facilityId} on {measDate}")

        sample_data = pd.DataFrame(data=data_list)

        sample_data.to_csv(f'data/env/{itemcode}_{fatr}_data.csv', encoding='utf-8-sig', index=False)


def main():
    serviceKey = 'cc9f5cd1181a40b3ac686421b352863d'

    # 토마토 작목 농가 정보 확인
    # check_farm_id(serviceKey, '080300')
    # tomato_id = pd.read_csv('data/id/080300_data.csv', encoding='utf-8-sig')
    # user_list = tomato_id['userId'].tolist()
    #
    # #토마토 농가 작기 확인
    # check_farm_season(serviceKey, user_list, '080300')
    # with open('data/season/080300_season_data.json', 'r', encoding='utf-8') as f:
    #     tomato_season = json.load(f)
    #
    #
    # #토마토 농가 환경 정보 확인
    # env_list = [('EI', 'IS'), ('EI', 'IR'), ('EI', 'LI'), ('EI', 'TI')
    #             , ('EI', 'HI'), ('EI', 'HI01'), ('EO', 'TE'), ('EO', 'HE'), ('EO', 'CR')]
    #
    # for x, y in env_list:
    #     check_farm_env(serviceKey, tomato_season, x, y, '080300')

    crop_id = pd.read_csv('data/id/tomato_cropping_season.csv', encoding='utf-8-sig')
    df_list = []

    for row in tqdm(crop_id.itertuples(index=False)):
        userId = row.facilityId[:-3]
        croppingSerlNo = row.croppingSerlNo
        startDate = row.croppingDate
        endDate = row.croppingEndDate


        url = f"http://www.smartfarmkorea.net/Agree_WS/webservices/ProvideRestService/getCultivateDataList/{serviceKey}/{userId}/{croppingSerlNo}/{startDate}/{endDate}"
        response = requests.get(url)
        data = response.json()

        df = pd.DataFrame(data)
        df_list.append(df)
        print(df.head())

    # 모든 농가의 생육 정보 데이터 합치기
    df_all = pd.concat(df_list, ignore_index=True)
    df_all.to_csv('data/cultivate/080300_cultivate_data.csv', index=False, encoding='utf-8-sig')



if __name__ == '__main__':
    main()