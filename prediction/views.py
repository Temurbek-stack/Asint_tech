from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(BASE_DIR, 'data')

model1 = joblib.load(os.path.join(data_path, 'GBM_MADEL_WITHOUT_DISTANCE.pkl'))
model2 = joblib.load(os.path.join(data_path, 'model2.pkl'))
x_columns = pd.read_csv(os.path.join(data_path, 'xcolumns.csv'))
uybor_cols = pd.read_csv(os.path.join(data_path, 'uybor_columns.csv'))
mahalla_and_tuman = pd.read_csv(os.path.join(data_path, 'mahalla_tuman_codes.csv'))
unique_mahalla_olx = pd.read_csv(os.path.join(data_path, 'unique_mahalla_olx.csv'))

@api_view(['POST'])
def predict_home_value(request):
    try:
        input_data = request.data
        my_dict = {col: 0 for col in x_columns.columns if col != 'Unnamed: 0'}

        my_dict["totalArea"] = input_data.get("area")
        my_dict["numberOfRooms"] = input_data.get("rooms")
        my_dict["floor"] = input_data.get("floor")
        my_dict["floorOfHouse"] = input_data.get("total_floors")
        my_dict["furnished"] = 1 if input_data.get("mebel") == 'Ha' else 0
        my_dict["handle"] = 1 if input_data.get("kelishsa") == 'Ha' else 0
        my_dict["pricingMonth"] = input_data.get("month")
        my_dict["pricingYear"] = input_data.get("year")

        for k, v in {
            "Maktab": "shkola", "Supermarket": "supermarket", "Do'kon": "magazini", "Park": "park"
        }.items():
            my_dict[v] = 1 if k in input_data.get("atrofda", []) else 0

        for k, v in {
            "Televizor": "tv_wm_ac_fridge", "Internet": "telefon_internet"
        }.items():
            my_dict[v] = 1 if k in input_data.get("uyda", []) else 0

        for prefix, val in [
            ("ownerType_", input_data.get("owner")),
            ("planType_", input_data.get("planirovka")),
            ("repairType_", input_data.get("renovation")),
            ("bathroomType_", input_data.get("sanuzel")),
            ("marketType_", input_data.get("bino_turi")),
            ("buildType_", input_data.get("qurilish_turi")),
        ]:
            if val:
                my_dict[f"{prefix}{val}"] = 1

        if input_data.get("district"):
            d = mahalla_and_tuman[mahalla_and_tuman['district_str'] == input_data['district']]['district_code'].values
            my_dict["district_code"] = d[0] if len(d) > 0 else 0
        if input_data.get("mahalla"):
            n = mahalla_and_tuman[mahalla_and_tuman['neighborhood_latin'] == input_data['mahalla']]['neighborhood_code'].values
            my_dict["neighborhood_code"] = n[0] if len(n) > 0 else 0

        model = model1 if input_data.get("mahalla") in set(unique_mahalla_olx['neighborhood_code']) else model2
        df = pd.DataFrame([my_dict])
        df['numberOfRooms'] = df['numberOfRooms'].astype(int)
        df['floor'] = df['floor'].astype(int)
        df['floorOfHouse'] = df['floorOfHouse'].astype(int)
        df['totalArea'] = df['totalArea'].astype(float)
        if 'district_code' in df.columns:
            df['district_code'] = df['district_code'].astype(int)
        if 'neighborhood_code' in df.columns:
            df['neighborhood_code'] = df['neighborhood_code'].astype(int)

        
        if model == model2:
            df = df[uybor_cols['Unnamed: 0'].tolist()]

        prediction = model.predict(df)[0]
        margin = round(prediction * 0.0361)

        return Response({
            'predicted_price': round(prediction),
            'range': [round(prediction - margin), round(prediction + margin)]
        })

    except Exception as e:
        return Response({'error': str(e)}, status=500)
