import requests
import pandas as pd
from tqdm import tqdm
import json

def main():
    serviceKey = 'cc9f5cd1181a40b3ac686421b352863d'

    # 농가 지역, 코드, 작목 확인 API 주소
    # id_url = f'http://www.smartfarmkorea.net/Agree_WS/webservices/ProvideRestService/getIdentityDataList/{serviceKey}'

    # 데이터 확인
    # response_id = requests.get(id_url)
    # if response.status_code == 200:
    #     data = response.json()
    #     print(data)
    # else:
    #     print(f"Error: {response.status_code} - {response.text}")

    # json_data = response_id.json()
    #
    # id_csv = pd.DataFrame.from_dict(json_data)
    #
    #
    # tomato_csv = id_csv[id_csv['itemCode'] == '080300']
    # print(tomato_csv)

    # tomato_user_list = tomato_csv['userId'].tolist()
    # print(tomato_user_list)

    # print(id_csv.head())
    # id_csv.to_csv('id_data.csv', index=False, encoding='utf-8-sig')

    # 작기정보 조회 API 주소 (사용자별 작기 일자 추출)
    # user_season = {}
    # error_count = 0
    #
    # for user in tqdm(tomato_user_list):
    #     try:
    #         season_url = f"http://www.smartfarmkorea.net/Agree_WS/webservices/ProvideRestService/getCroppingSeasonDataList/{serviceKey}/{user}"
    #         response_s = requests.get(season_url)
    #         data = response_s.json()
    #         start_date = data[0]['croppingDate']
    #         end_date = data[0]['croppingEndDate']
    #
    #         # 날짜 범위 생성
    #         date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    #
    #         # 문자열 리스트로 변환
    #         date_list = date_range.strftime('%Y-%m-%d').tolist()
    #
    #         # 사용자별 날짜 리스트 저장
    #         user_season[user] = date_list
    #
    #     except ValueError as e:
    #         print(f"ValueError: {e}")
    #         print(data)
    #         error_count += 1

    # print(user_season)

    # with open('season_data.json', 'w', encoding='utf-8') as f:
    #     json.dump(user_season, f, ensure_ascii=False, indent=2)
    #
    # # 35 농가 작기 날짜 데이터 이상
    # print(error_count)


    # 데이터 확인
    # 환경정보 조회 API 주소
    id_data = pd.read_csv('id_data.csv', encoding='utf-8-sig')
    id_data = id_data[id_data['itemCode'] == '080300']
    id_list = id_data['userId'].tolist()
    id_list = id_list[100:105]

    season_data = json.load(open('season_data.json', 'r', encoding='utf-8'))



    data_list = []

    for i in tqdm(id_list):
        for j in season_data[i]:
            # 시설 id
            facilityId = i + "_01"
            # 측정일자 (season_data.json에 저장된 날짜)
            measDate = j
            # 분야코드(시설원예=FG)
            fldCode = "FG"
            # 분류코드(내부환경=EI)
            sectCode = "EI"
            # 항목코드(내부온도=TI)
            fatrCode = "TI"
            # 작물코드(토마토=80300)
            itemCode = "80300"

            try:
                env_url = f'http://www.smartfarmkorea.net/Agree_WS/webservices/ProvideRestService/getEnvDataList/{serviceKey}/{facilityId}/{measDate}/{fldCode}/{sectCode}/{fatrCode}/{itemCode}'

                result = requests.get(env_url).json()
                data_list.append(result)

            except Exception as e:
                print(f"Error fetching data for {facilityId} on {measDate}: {e}")


    sample_data = pd.DataFrame(data=data_list)

    sample_data.to_csv('sample_data.csv', encoding='utf-8-sig', index=False)





if __name__ == '__main__':
    main()