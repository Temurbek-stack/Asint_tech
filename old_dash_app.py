import dash
from dash import dcc, html, callback_context, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import dash_daq as daq 
from dash.dependencies import Input, Output, State
import json
import pandas as pd 
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import arrow_function, assign, Namespace
import joblib
import time
from pdf_generator import create_report
from pdf_generator_auto import create_report_auto
from dash.exceptions import PreventUpdate
import os
from datetime import datetime

def load_prediction_counts():
    try:
        file_path = os.path.join('data', 'prediction_counts.json')
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                events = json.load(f)
                if not isinstance(events, list):
                    events = []
                return events
        else:
            save_prediction_counts([])
            return []
    except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
        print(f"Error loading prediction counts: {str(e)}")
        return []

def save_prediction_counts(events):
    try:
        file_path = os.path.join('data', 'prediction_counts.json')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(events, f, indent=2)
    except Exception as e:
        print(f"Error saving prediction counts: {str(e)}")

def add_prediction_event(event_type):
    try:
        events = load_prediction_counts()
        new_event = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'home': 1 if event_type == 'home_predict' else 0,
            'auto': 1 if event_type == 'auto_predict' else 0,
            'home_downloads': 1 if event_type == 'home_download' else 0,
            'auto_downloads': 1 if event_type == 'auto_download' else 0
        }
        events.append(new_event)
        save_prediction_counts(events)
        print(f"\n[Link {event_type.split('_')[0].title()}] New {event_type.split('_')[1]} event recorded")
    except Exception as e:
        print(f"Error adding prediction event: {str(e)}")

# Initialize the prediction counts at startup
prediction_events = load_prediction_counts()

####################################################################################
####################################################################################
car_body_enginevol = pd.read_csv('data/data_to_find_enginevol_body.csv')
unique_mahalla_olx = pd.read_csv('data/unique_mahalla_olx.csv')
uybor_cols=pd.read_csv('data/uybor_columns.csv')
mahalla_and_tuman=pd.read_csv('data/mahalla_tuman_codes.csv')
# df = pd.read_csv(r'data\olx_data.csv')

model1 = joblib.load('data/GBM_MADEL_WITHOUT_DISTANCE.pkl')
model2 = joblib.load('data/model2.pkl')

model3 = joblib.load('data/CHEVROLET_DAEWOO_RAVON_LGBM_41.pkl')

model4 = joblib.load('data/CLEANDED_DATA_FOREIGN_LGBM.pkl')
X = pd.read_csv(r'data/xcolumns.csv')
model = model1

brand_car_names = pd.read_csv('data/Brand_and_car_column.csv')
X1 = pd.read_csv(r'data/Chevrolet_DAEWOO_RAVON_columns.csv')

X2 = pd.read_csv(r'data/FOREIGN_columns_cleaned_Data_lgbm.csv')

scaler1 = joblib.load('data/scaler_CHEVROLET-DAEWOO-RAVON.pkl')

scaler2 = joblib.load('data/scaler_foreign_cleaned_Data_lgbm.pkl')

my_dict1 = {} # so columns and zerod values are saved here 
for key in X1.columns:
    my_dict1[key]=0
del my_dict1['Unnamed: 0']


my_dict2 = {} # so columns and zerod values are saved here 
for key in X2.columns:
    my_dict2[key]=0
del my_dict2['Unnamed: 0']
#########################x_train['brand_type']

from datetime import datetime

print(datetime)  # Should output: <class 'datetime.datetime'>

current_month = datetime.now().month
current_year = datetime.now().year

print(f"Current Month: {current_month}, Current Year: {current_year}")

# df['month_and_year'] = pd.to_datetime(df['month_and_year'], format='%b-%y').dt.strftime('%m-%Y')
# df['month_and_year'] = pd.to_datetime(df['month_and_year'], format='%m-%Y')
# df_sorted = df.sort_values(by='month_and_year')
# df_sorted['price_per_sq'] = df_sorted['price1']/df_sorted['sqrm1']

my_dict3 = {}

for key in X.columns:
    if key != 'Unnamed: 0':
        my_dict3[key]=0
#########################
# my_dict_xls = pd.DataFrame().from_dict(my_dict)
# my_dict_xls.to_excel('my_dict_xls.xlsx')

importances = model1.feature_importance()
# print(len(importances))
feature_importances = pd.DataFrame({'Feature': my_dict3.keys(), 'Importance': importances})
top_20_features = feature_importances.sort_values(by='Importance', ascending=False).head(50)

barh = px.bar(top_20_features, x='Importance', y = 'Feature', orientation='h')
barh.update_layout(
        xaxis_title="Muhimlik darajasi",
        xaxis_gridcolor='lightblue',
        yaxis_gridcolor='lightblue',
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
barh.update_xaxes(showgrid=True, gridcolor='lightblue', gridwidth=1, griddash='dash')
barh.update_yaxes(showgrid=True, gridcolor='lightblue', gridwidth=1, griddash='dash')

#########################

# avg_price = df_sorted.groupby(['month_and_year', 'Type of housing'])['price1'].mean().reset_index()
# countOfposting = df_sorted.groupby(['month_and_year', 'Type of housing']).size().reset_index(name='count')
# aggregated_df = df_sorted.groupby(['Количество комнат:', 'Type of housing']).size().reset_index(name='count')


####################################################################################
####################################################################################


app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP], 
    external_scripts=['./assets/dashExtensions_default.js'],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
    title='Link Assets',  # This sets the tab text
    assets_folder='assets'
)
# server = app.server
app.config.suppress_callback_exceptions = True

####################################################################################
####################################################################################

#---- Info tab Link Home----#
info_tab_home = html.Div([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H2("Link Home", 
                    className='custom-telegraf',
                    style={
                        'color': '#003049',
                        'fontSize': '32px',
                        'marginBottom': '30px',
                        'textAlign': 'center'
                    }
                ),
                html.P(
                "Link Home – bu ko'chmas mulk obyektlarini avtomatik baholash platformasi bo'lib, sun'iy intellekt texnologiyalari asosida uylar, kvartiralar va boshqa turar-joy obyektlarining* bozor qiymatini tezkor va aniq hisoblab beradi. Platforma real bozor ma'lumotlari, geospatial tahlillar va boshqa muhim ko'rsatkichlardan foydalanadi.",                    style={'fontSize': '16px', 'marginBottom': '30px', 'lineHeight': '1.6'}
                ),
                html.H3("Nega bizga Link Home kerak?", style={'color': '#003049', 'fontSize': '24px', 'marginBottom': '20px'}),
                html.P(
                    "Ko'chmas mulk baholash jarayoni an'anaviy usulda uzoq vaqt talab qiladi, subyektiv yondashuvga ega va ko'pincha qimmatga tushadi. Shu sababli, baholash jarayonini avtomatlashtirish quyidagi muammolarni hal qilishga yordam beradi:",
                    style={'fontSize': '16px', 'marginBottom': '15px'}
                ),
                html.Ul([
                    html.Li("Baholash jarayonining uzoq davom etishi.", style={'marginBottom': '10px'}),
                    html.Li("Inson omili tufayli yuzaga keladigan xatoliklar va subyektivlik.", style={'marginBottom': '10px'}),
                    html.Li("Yuqori xizmat narxlari.", style={'marginBottom': '10px'}),
                    html.Li("Baholash natijalarining shaffof emasligi.", style={'marginBottom': '10px'})
                ], style={'marginBottom': '30px', 'paddingLeft': '20px'}),
                html.P(
                    "Link Home ushbu muammolarni hal qilib, tezkor, ishonchli va arzon baholash tizimini taklif etadi.",
                    style={'fontSize': '16px', 'marginBottom': '40px'}
                ),
                html.Img(src="assets/linkhome1.png", style={'width': '100%', 'marginBottom': '40px'}),

                html.H3("Qo'llanilish sohalari", style={'color': '#003049', 'fontSize': '24px', 'marginBottom': '20px'}),
                html.Ul([
                    html.Li("Banklar – garov mulklarini tezkor baholash va aktivlarni samarali boshqarish.", style={'marginBottom': '10px'}),
                    html.Li("Sug'urta kompaniyalari – uy-joy sug'urtasi va zararni hisoblash jarayonlarini tezlashtirish.", style={'marginBottom': '10px'}),
                    html.Li("Davlat tashkilotlari – soliq va shaharsozlik maqsadlarida ko'chmas mulk baholarini aniqlash.", style={'marginBottom': '10px'}),
                    html.Li("Investorlar – ko'chmas mulk portfellarini samarali baholash.", style={'marginBottom': '10px'}),
                    html.Li("Ko'chmas mulk agentliklari – mijozlar uchun tezkor narx taklif qilish va bozor monitoringi.", style={'marginBottom': '10px'})
                ], style={'marginBottom': '40px', 'paddingLeft': '20px'}),

                html.H3("Link Home qanday ishlaydi?", style={'color': '#003049', 'fontSize': '24px', 'marginBottom': '20px'}),
                html.P(
                    "Foydalanuvchilar o'zlari baholashni xohlagan ko'chmas mulk obyektining asosiy ma'lumotlarini kiritadilar. Platforma esa sun'iy intellekt va katta hajmdagi ma'lumotlar tahliliga asoslangan model yordamida bir necha soniya ichida bozor qiymatini hisoblab beradi.",
                    style={'fontSize': '16px', 'marginBottom': '40px', 'lineHeight': '1.6'}
                ),
                html.P(
                "Bizning modelimiz so'nggi ikki yil ichida 2 milliondan ortiq bozor kuzatuvlari asosida o'qitilgan bo'lib, aniqlik darajasi 95 foizdan yuqori.",                    style={'fontSize': '16px', 'marginBottom': '40px', 'lineHeight': '1.6'}
                ),
                html.Img(src="assets/linkhome2.png", style={'width': '100%', 'marginBottom': '40px'}),
                html.P(
                "Bizning modelimiz so'nggi ikki yil ichida 2 milliondan ortiq bozor kuzatuvlari asosida o'qitilgan bo'lib, aniqlik darajasi 95 foizdan yuqori.",                    style={'fontSize': '16px', 'marginBottom': '40px', 'lineHeight': '1.6'}
                ),
                html.H3("Nega aynan Link Home?", style={'color': '#003049', 'fontSize': '24px', 'marginBottom': '20px'}),
                html.Ul([
                    html.Li("Tezkor va ishonchli natijalar", style={'marginBottom': '10px'}),
                    html.Li("Sun'iy intellekt yordamida shaffof va obyektiv baholash", style={'marginBottom': '10px'}),
                    html.Li("Bozor ma'lumotlari va geospatial tahlillarni hisobga olgan holda maksimal aniqlik", style={'marginBottom': '10px'}),
                    html.Li("Qimmat va uzoq davom etadigan an'anaviy baholash jarayoniga ehtiyoj yo'q", style={'marginBottom': '10px'}),
                ], style={'marginBottom': '40px', 'paddingLeft': '20px'}),

                html.H3("Platformadan foydalanish usullari", style={'color': '#003049', 'fontSize': '24px', 'marginBottom': '20px'}),
                html.P("Bizneslar (B2B) – obuna asosida yoki API orqali integratsiya qilish (Pay-per-use modeli). Ya'ni tashkilotlar Link Home'ni o'z tizimlariga qo'shib, baholash jarayonlarini avtomatlashtirishlari mumkin.", 
                    style={'fontSize': '16px', 'marginBottom': '20px', 'lineHeight': '1.6'}),
                html.P("Jismoniy shaxslar – individual ehtiyojlariga qarab baholash xizmatidan foydalanishlari va natijalarni yuklab olishlari mumkin.", 
                    style={'fontSize': '16px', 'marginBottom': '40px', 'lineHeight': '1.6'}),

                html.P("*Bugungi kunda Link Home modeli orqali faqat Toshkent shahridagi ko'p qavatli turarjoylarni baholashingiz mumkin.",
                    style={'fontSize': '14px', 'color': '#7F8C8D', 'fontStyle': 'italic', 'marginBottom': '40px'}),
                
                html.P("Yangiliklarni bizning ijtimoiy tarmoqlarda kuzatib boring.", 
                    style={'fontSize': '16px', 'marginBottom': '10px', 'fontWeight': 'bold'}),  # Bold text

                dbc.Row([
                    dbc.Col(html.A(
                        html.Img(src='https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png', 
                                height='40px'),  # Instagram logo
                        href='https://www.instagram.com/linkdatauz', target='_blank'
                    ), width='auto'),
                    
                    dbc.Col(html.A(
                        html.Img(src='https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg', 
                                height='40px'),  # Telegram logo
                        href='https://t.me/linkdatauz', target='_blank'
                    ), width='auto'),
                    
                    dbc.Col(html.A(
                        html.Img(src='https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png', 
                                height='40px'),  # LinkedIn logo
                        href='https://www.linkedin.com/company/link-data/posts/?feedView=all', target='_blank'
                    ), width='auto'),
            
], style={'textAlign': 'center', 'marginTop': '20px'}),

                # Add after the title in the home section
                html.Div([
                    html.H4("Jami baholashlar soni", className="text-center mb-2"),
                    html.H2(id='home-prediction-count', 
                            className="text-center",
                            style={'fontSize': '48px', 'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#00264D'})
                ], style={'textAlign': 'center', 'marginBottom': '20px'}),
            ], className='custom-opensauce', style={
                'maxWidth': '1200px',
                'margin': '0 auto',
                'padding': '40px',
                'backgroundColor': 'white',
                'borderRadius': '10px',
                'marginTop': '20px',
                'marginBottom': '40px'
            })
        ], xs=12, sm=12, md=12, lg=12)
    ])
], style={'backgroundColor': 'white', 'minHeight': '100vh', 'padding': '20px'})






#---- Info tab Link Auto----#
info_tab_auto = html.Div([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H2("Link Auto", 
                    className='custom-telegraf',
                    style={
                        'color': '#003049',
                        'fontSize': '32px',
                        'marginBottom': '30px',
                        'textAlign': 'center'
                    }
                ),
                html.P(
                    "Link Auto – avtomobillarni avtomatik baholash platformasi bo'lib, mashinalarning bozor qiymatini tezkor va aniq aniqlashga yordam beradi. Sun'iy intellekt asosida ishlovchi modelimiz transport vositasining markasi, yili, yurilgan masofasi, holati, bozordagi talab va 50 dan ortiq boshqa omillarni hisobga olib, eng optimal bahoni taqdim etadi.",
                    style={
                        'fontSize': '16px',
                        'marginBottom': '30px',
                        'lineHeight': '1.6'
                    }
                ),
                html.H3(
                    "An'anaviy avtomobil baholash jarayonlari quyidagi muammolarga duch keladi:",
                    style={
                        'color': '#003049',
                        'fontSize': '24px',
                        'marginBottom': '20px',
                        'marginTop': '40px'
                    }
                ),
                html.Ul([
                    html.Li("Inson omiliga bog'liq bo'lgan subyektiv yondashuv.", 
                        style={'marginBottom': '10px'}),
                    html.Li("Bozor sharoitlarining doimiy o'zgarib borishi.", 
                        style={'marginBottom': '10px'}),
                    html.Li("Baholash jarayonining uzoq davom etishi.", 
                        style={'marginBottom': '10px'}),
                    html.Li("Baholovchilarga bog'liq yuqori xarajatlar.", 
                        style={'marginBottom': '10px'})
                ], style={'marginBottom': '30px', 'paddingLeft': '20px'}),
                html.P(
                    "Link Auto ushbu muammolarni bartaraf etib, tezkor, shaffof va aniq baholash imkonini yaratadi.",
                    style={
                        'fontSize': '16px',
                        'marginBottom': '40px'
                    }
                ),
                html.Img(src="assets/linkauto1.png", 
                    style={'width': '100%', 'borderRadius': '10px', 'marginBottom': '40px'}),
                html.H3(
                    "Qo'llanilish sohalari",
                    style={
                        'color': '#003049',
                        'fontSize': '24px',
                        'marginBottom': '20px'
                    }
                ),
                html.Ul([
                    html.Li("Banklar – avtokreditlar va garov mulklarini baholash.", 
                        style={'marginBottom': '10px'}),
                    html.Li("Sug'urta kompaniyalari – avtotransport sug'urtasi va zarar hisob-kitoblari.", 
                        style={'marginBottom': '10px'}),
                    html.Li("Avtosalonlar va avtokredit kompaniyalari – mashinalarning bozor narxini tezkor aniqlash.", 
                        style={'marginBottom': '10px'}),
                    html.Li("Online avtomobil savdo platformalari – avtomobil bahosini avtomatlashtirilgan tarzda ko'rsatish.", 
                        style={'marginBottom': '10px'}),
                    html.Li("Hukumat tashkilotlari – bojxona va soliq hisob-kitoblarida avtomobil narxlarini baholash.", 
                        style={'marginBottom': '10px'})
                ], style={'marginBottom': '40px', 'paddingLeft': '20px'}),
                html.H3(
                    "Link Auto qanday ishlaydi?",
                    style={
                        'color': '#003049',
                        'fontSize': '24px',
                        'marginBottom': '20px'
                    }
                ),
                html.P(
                    "Foydalanuvchilar o'z avtomobilining asosiy parametrlarini kiritadilar va bir necha soniya ichida tizim ularga bozor qiymatini hisoblab beradi.",
                    style={
                        'fontSize': '16px',
                        'marginBottom': '40px',
                        'lineHeight': '1.6'
                    }
                    
                ),
                html.P(
                        "Link Auto modeli real bozor ma'lumotlari va ilg'or sun'iy intellekt algoritmlaridan foydalangan holda ishlaydi. 2023-yilda ishga tushirilgan dastlabki modeldan keyin, hozirgi kunda Link Auto 3.0 modeliga o'tganmiz va aniqlik darajasi 95 foizdan yuqorilashgan." ,
                        style={
                        'fontSize': '16px',
                        'marginBottom': '40px',
                        'lineHeight': '1.6'
                    }),
                html.Img(src="assets/linkauto2.png", 
                    style={'width': '100%', 'borderRadius': '10px', 'marginBottom': '40px'}),
                html.H3("Nega aynan Link Auto?", style={'color': '#003049', 'fontSize': '24px', 'marginBottom': '20px'}),
                html.Ul([
                    html.Li("Bozor sharoitlariga tezkor moslashuv – model doimiy ravishda bozor ma'lumotlari bilan yangilanadi", style={'marginBottom': '10px'}),
                    html.Li("Tez va ishonchli natijalar – foydalanuvchilar bir necha soniya ichida natijaga ega bo'ladilar", style={'marginBottom': '10px'}),
                    html.Li("Shaffoflik va subyektivlikdan holi baholash – inson omilidan mustaqil ishlaydi", style={'marginBottom': '10px'}),
                    html.Li("Qimmat va uzoq davom etadigan an'anaviy baholash jarayoniga ehtiyoj yo'q", style={'marginBottom': '10px'}),
                ], style={'marginBottom': '40px', 'paddingLeft': '20px'}),
                html.H3("Platformadan foydalanish usullari", style={'color': '#003049', 'fontSize': '24px', 'marginBottom': '20px'}),
                html.Ul([
                    html.Li("Bizneslar (B2B) – obuna asosida yoki API orqali integratsiya qilish (Pay-per-use modeli). Tashkilotlar Link Auto'ni o'z tizimlariga qo'shib, baholash jarayonlarini avtomatlashtirishlari mumkin.", style={'marginBottom': '10px'}),
                    html.Li("Jismoniy shaxslar – avtomobilini sotmoqchi yoki sotib olmoqchi bo'lgan shaxslar uchun tezkor baholash xizmati.", style={'marginBottom': '10px'}),



               html.P("Yangiliklarni bizning ijtimoiy tarmoqlarda kuzatib boring.", 
                    style={'fontSize': '16px', 'marginBottom': '10px', 'fontWeight': 'bold'}),  # Bold text

                dbc.Row([
                    dbc.Col(html.A(
                        html.Img(src='https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png', 
                                height='40px'),  # Instagram logo
                        href='https://www.instagram.com/linkdatauz', target='_blank'
                    ), width='auto'),
                    
                    dbc.Col(html.A(
                        html.Img(src='https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg', 
                                height='40px'),  # Telegram logo
                        href='https://t.me/linkdatauz', target='_blank'
                    ), width='auto'),
                    
                    dbc.Col(html.A(
                        html.Img(src='https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png', 
                                height='40px'),  # LinkedIn logo
                        href='https://www.linkedin.com/company/link-data/posts/?feedView=all', target='_blank'
                    ), width='auto'),
            
], style={'textAlign': 'center', 'marginTop': '20px'})


                    
                ], style={'marginBottom': '40px', 'paddingLeft': '20px'}),

            ], className='custom-opensauce', style={
                'maxWidth': '1200px',
                'margin': '0 auto',
                'padding': '40px',
                'backgroundColor': 'white',
                'borderRadius': '10px',
                'marginTop': '20px',
                'marginBottom': '40px'
            })
        ], xs=12, sm=12, md=12, lg=12)
    ])
], style={
    'backgroundColor': 'white',
    'minHeight': '100vh',
    'padding': '20px'
})


















#####################################################################################

#---- dropdown for tumanlar----#
unique_dis = mahalla_and_tuman['district_str'].unique().tolist()
dropdown_tuman = [{'label': district, 'value': district} for district in unique_dis]

#---- prediction tab Link Home----#
prediction_home = dbc.Row([
    dbc.Col([
        html.Div(
            id='input-panel',
            className='custom-opensauce',
            style={
                'position': 'relative',
                'left': '0',
                'top': '50%',
                'transform': 'translateY(-50%)',
                'padding': '20px',
                'width': '100%',
                #'margin-top': '20px',
                'margin-bottom': '20px',
                'color': 'black',
                'font-weight': 'bold',
                'border': 'none'
            },            
            children=[


########################################################################################
                html.Label('Tuman va mahallani tanlang', style={'display': 'block', 'font-weight': 'bold', 'margin-bottom': '5px'}),
                html.Div(
                    style={
                        'background-color': '#ffffff',
                        #'padding': '10px',
                        'border-radius': '30px',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        'display': 'flex',  # Makes items align in a row
                        #'gap': '10px'  # Adds space between the dropdowns
                    },
                    children=[
                        html.Div([
                            dcc.Dropdown(
                                id='district-dropdown',
                                options=dropdown_tuman,
                                placeholder='Tumanni tanlang',
                                style={
                                'width': '100%',  
                                'border-radius': '30px 0px 0px 30px',  # Makes edges rounded
                                #'border': '1px solid #ccc',
                                #'padding': '8px'  # Optional: Adds spacing for better appearance
                                }
                            )
                        ], style={'flex': 1}),  # Makes both dropdowns take equal width
                        
                        html.Div([
                            dcc.Dropdown(
                                id='mahalla-dropdown',
                                placeholder='Mahallani tanlang',
                                style={
                                'width': '100%',  
                                'border-radius': '0px 30px 30px 0px',  # Makes edges rounded
                                #'border': '1px solid #ccc',
                                'border-left': '0px', #'border': '1px solid #ccc',  # Optional: Adjust border color
                                #'padding': '8px'  # Optional: Adds spacing for better appearance
                                }
                            )
                        ], style={'flex': 1})  # Equal width for mahalla dropdown
                    ]
                ),
################################################################################


                html.Label(
            'Umumiy maydoni  va Xonalar soni', style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}
        ),
                html.Div(
                    style={
                        'background-color': '#ffffff',
                        #'padding': '15px',
                        'border-radius': '20px',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        'display': 'flex',  # Places inputs next to each other
                        #'gap': '10px',  # Adds space between them
                    },
                    children=[
                        html.Div(
                            style={'width': '50%'},  # Each input takes 50% of the width
                            children=[
                                #html.Label('Umumiy maydoni (m2) va Xonalar soni',
                                 #           style={'font-weight': 'bold','font-size': '13px'}),
                                dcc.Input(
                                    id='area-input', 
                                    type='number', 
                                    placeholder='Umumiy maydoni (m2)', 
                                      style={
                            'width': '100%',  
                            'border-radius': '30px 0px 0px 30px',  # Makes edges rounded
                            'border': '1px solid #ccc',
                            #'border': '1px solid #ccc',  # Optional: Adjust border color
                            'padding': '6px'  # Optional: Adds spacing for better appearance
                        }
                                ),
                            ]
                        ),
                        html.Div(
                            style={'width': '50%'},  
                            children=[
                                # html.Label('Xonalar soni', style={'font-weight': 'bold'}),
                                dcc.Input(
                                    id='rooms-input', 
                                    type='number', 
                                    placeholder='Xonalar soni', 
                                    style={
                                'width': '100%',  
                                'border-radius': '0px 30px 30px 0px',
                                'border': '1px solid #ccc',
                                'border-left': '0px',  # Makes edges rounded
                                'padding': '6px'  # Optional: Adds spacing for better appearance
                                }
                                ),
                            ]
                        ),
                    ]
                ),

############################################################################################################
                html.Label(
        'Nechinchi qavat va Uy qavatlari soni', style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}
    ),

                html.Div(
                    style={
                        'background-color': '#ffffff',
                        #'padding': '15px',
                        'border-radius': '20px',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        'display': 'flex',  # Places inputs next to each other
                        #'gap': '10px',  # Adds space between them
                    },
                    children=[
                        dcc.Input(
                            id='floor-input', 
                            type='number', 
                            placeholder='Nechinchi qavat', 
                            className='no-bold-placeholder',
                             style={
                            'width': '50%',  
                            'border-radius': '30px 0px 0px 30px',  # Makes edges rounded
                            'border': '1px solid #ccc', #'border': '1px solid #ccc',  # Optional: Adjust border color
                            'padding': '6px'  # Optional: Adds spacing for better appearance
                        }
                        ),
                        dcc.Input(
                            id='total-floors-input', 
                            type='number', 
                            placeholder='Uy qavatlari soni', 
                                style={
                            'width': '50%',  
                            'border-radius': '0px 30px 30px 0px',
                            'border': '1px solid #ccc',
                            'border-left': '0px',   # Makes edges rounded
                            'padding': '6px'  # Optional: Adds spacing for better appearance
                        }
                        ),
                    ]
                ),

###############################################################################################################
            
                #----yaqin atrofda
                html.Label('Atrofda nimalar bor', style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}),
                dcc.Dropdown(
                    id='atrofda-dropdown',
                    options=[
                        {'label': 'Maktab', 'value': 'Maktab'},
                        {'label': 'Supermarket', 'value': 'Supermarket'},
                        {'label': "Do'kon", 'value': "Do'kon"},
                        {'label': 'Avtoturargoh', 'value': 'Avtoturargoh'},
                        {'label': 'Shifoxona', 'value': 'Shifoxona'},
                        {'label': 'Poliklinika', 'value': 'Poliklinika'},
                        {'label': 'Bekat', 'value': 'Bekat'},
                        {'label': 'Bolalar maydonchasi', 'value': 'Bolalar maydonchasi'},
                        {'label': 'Restoran', 'value': 'Restoran'},
                        {'label': 'Kafe', 'value': 'Kafe'},
                        {'label': "Ko'ngilochar maskanlar", 'value': "Ko'gilochar maskanlar"},
                        {'label': "Bog'cha", 'value': "Bog'cha"},
                        {'label': 'Yashil hudud', 'value': 'Yashil hudud'},
                        {'label': 'Park', 'value': 'Park'}
                    ],
                    multi=True,
                    placeholder='Atrofda nimalar bor',
                    style={
                        'background-color': '#ffffff',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        #'padding': '10px',
                        'width': '100%',  # Make it full width
                        #'backgroundColor': '#f8f9fa',  # Light gray background
                        'border-radius': '30px',  # Rounded edges
                        #'border': '1px solid #ccc',  # Subtle border
                        #'fontSize': '16px'  # Bigger text
                        #'color': '#333'  # Darker text color
                    },
                ),

################################################################################################################

                #---- mebellimi yo'qmi
                html.Label('Jihozlanganmi', style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}),
                dbc.RadioItems(
                    id='mebel-dropdown',
                    options=[
                        {'label': 'Ha', 'value': 'Ha'},
                        {'label': "Yo'q", 'value': "Yo'q"},
                    ],
                    value='Ha',  # Default selected
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                    style={'whiteSpace': 'nowrap', 'flexWrap': 'wrap'}  # Added flexWrap here as well           
                ),
################################################################################################################              

                #----uydagi jihozlar
                html.Label('Uyda nimalar bor', style={'display': 'block', 'font-weight': 'bold', 'margin-bottom': '5px', 'margin-top': '10px'}),
                dcc.Dropdown(
                    id='uyda-dropdown',
                    options=[
                        {'label': 'Sovutgich', 'value': 'Sovutgich'},
                        {'label': 'Telefon', 'value': 'Telefon'},
                        {'label': 'Oshxona', 'value': 'Oshxona'},
                        {'label': 'Kabel TV', 'value': 'Kabel TV'},
                        {'label': 'Internet', 'value': 'Internet'},
                        {'label': 'Balkon', 'value': 'Balkon'},
                        {'label': 'Kir yuvish mashinasi', 'value': 'Kir yuvish mashinasi'},
                        {'label': 'Konditsioner', 'value': 'Konditsioner'},
                        {'label': 'Televizor', 'value': 'Televizor'}
                    ],
                    multi=True,
                    placeholder='Uyda nimalar bor',
                    style={
                        'background-color': '#ffffff',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        #'padding': '10px',
                        'width': '100%',  # Make it full width
                        #'backgroundColor': '#f8f9fa',  # Light gray background
                        'border-radius': '30px',  # Rounded edges
                        #'border': '1px solid #ccc',  # Subtle border
                        #'fontSize': '16px'  # Bigger text
                        #'color': '#333'  # Darker text color
                    },
                ),
                #----qurilish turi
                html.Label("Qurilish turi", style={'display': 'block', 'font-weight': 'bold', 'margin-bottom': '5px', 'margin-top': '10px'}),
                dcc.Dropdown(
                    id='qurilish-turi-dropdown',
                    options=[
                        {'label': 'Blokli', 'value': 'Blokli'},
                        {'label': "G'ishtli", 'value': 'G_ishtli'},
                        {'label': 'Monolitli', 'value': 'Monolitli'},
                        {'label': 'Panelli', 'value': 'Panelli'},
                        {'label': "Yog'ochli", 'value': 'Yog_ochli'}
                    ],
                    placeholder='Qurilish turi',
                    style={
                        'background-color': '#ffffff',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        #'padding': '10px',
                        'width': '100%',  # Make it full width
                        #'backgroundColor': '#f8f9fa',  # Light gray background
                        'border-radius': '30px',  # Rounded edges
                        #'border': '1px solid #ccc',  # Subtle border
                        #'fontSize': '16px'  # Bigger text
                        #'color': '#333'  # Darker text color
                    },
                ),
                #---- planirovka turi
                html.Label('Planirovka turi', style={'display': 'block', 'font-weight': 'bold', 'margin-bottom': '5px', 'margin-top': '10px'}),
                dcc.Dropdown(
                    id='planirovka-dropdown',
                    options=[
                        {'label': 'Alohida ajratilgan', 'value': 'Alohida_ajratilgan'},
                        {'label': 'Aralash', 'value': 'Aralash'},
                        {'label': 'Aralash alohida', 'value': 'Aralash_alohida'},
                        {'label': 'Kichik oilalar uchun', 'value': 'Kichik_oilalar_uchun'},
                        {'label': 'Ko\'p darajali', 'value': 'Ko_p_darajali'},
                        {'label': 'Pentxaus', 'value': 'Pentxaus'},
                        {'label': 'Studiya', 'value': 'Studiya'}
                    ],
                    placeholder='Planirovka turi',
                    style={
                        'background-color': '#ffffff',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        #'padding': '10px',
                        'width': '100%',  # Make it full width
                        #'backgroundColor': '#f8f9fa',  # Light gray background
                        'border-radius': '30px',  # Rounded edges
                        #'border': '1px solid #ccc',  # Subtle border
                        #'fontSize': '16px'  # Bigger text
                        #'color': '#333'  # Darker text color
                    },
                ),
                #---- sanuzel turi
                html.Label('Sanuzel turi', style={'display': 'block', 'font-weight': 'bold', 'margin-bottom': '5px', 'margin-top': '10px'}),
                dcc.Dropdown(
                    id='sanuzel-dropdown',
                    options=[
                        {'label': "2 va undan ko'p sanuzel", 'value': '2_va_undan_ko_p_sanuzel'},
                        {'label': 'Alohida', 'value': 'Alohida'},
                        {'label': 'Aralash', 'value': 'Aralash'}
                    ],
                    placeholder='Sanuzel turi',
                    style={
                        'background-color': '#ffffff',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        #'padding': '10px',
                        'width': '100%',  # Make it full width
                        #'backgroundColor': '#f8f9fa',  # Light gray background
                        'border-radius': '30px',  # Rounded edges
                        #'border': '1px solid #ccc',  # Subtle border
                        #'fontSize': '16px'  # Bigger text
                        #'color': '#333'  # Darker text color
                    },
                ),
################################################################################
                html.Div(
                    #style={'display': 'flex', 'flex-direction': 'column', 'gap': '20px'},
                    children=[
                        html.Div(
                            style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'flex-start'},
                            children=[
                                html.Label('Kim egalik qiladi', style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}),
                                html.Div(
                                    style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px', 'width': '100%'},  # Make buttons horizontal
                                    children=[
                                        dbc.RadioItems(
                                            id='owner-dropdown',
                                            options=[
                                                {'label': 'Biznes', 'value': 'Biznes'},
                                                {'label': "Xususiy", 'value': "Xususiy"},
                                            ],
                                            value='Xususiy',
                                            className="btn-group",
                                            inputClassName="btn-check",
                                            labelClassName="btn btn-outline-primary",
                                            labelCheckedClassName="active",
                                            style={'whiteSpace': 'nowrap', 'flexWrap': 'wrap'}  # Added flexWrap here as well
                                        ),
                                    ]
                                ),
                            ]
                        ),

                        html.Div(
                            style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'flex-start'},
                            children=[
                                html.Label("Ta'mir turi", style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}),
                                html.Div(
                                    style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px', 'width': '100%'},  # Added width: 100% to ensure proper wrapping
                                    children=[
                                        dbc.RadioItems(
                                            id='renovation-dropdown',
                                            options=[
                                                {'label': "Zo'r", 'value': 'Zo_r'},
                                                {'label': 'Yaxshi', 'value': 'Yaxshi'},
                                                {'label': 'Qoniqarsiz', 'value': 'Qoniqarsiz'}
                                            ],
                                            value='Yaxshi',
                                            className="btn-group",
                                            inputClassName="btn-check",
                                            labelClassName="btn btn-outline-primary",
                                            labelCheckedClassName="active",
                                            style={'whiteSpace': 'nowrap', 'flexWrap': 'wrap'}  # Added flexWrap here as well
                                        ),
                                    ]
                                ),
                            ]
                        )
                    ]
                ),


                #----bino turi
                html.Div(
                    #style={'display': 'flex', 'flex-direction': 'column', 'gap': '10px'},
                    children=[
                        # Bozor turi
                        html.Label('Bozor turi', style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}),
                        dbc.RadioItems(
                            id='bino-turi-dropdown',
                            options=[
                                {'label': 'Ikkilamchi bozor', 'value': 'Ikkilamchi_bozor'},
                                {'label': 'Yangi qurilgan', 'value': 'Yangi_qurilgan_uylar'}
                            ],
                            value='Ikkilamchi_bozor',  # Set a default value
                            className="btn-group",
                            inputClassName="btn-check",
                            labelClassName="btn btn-outline-primary",
                            labelCheckedClassName="active",
                            style={
                                'whiteSpace': 'nowrap',
                                'flexWrap': 'wrap',
                                'fontSize': '14px',  # Default font size
                                '@media (max-width: 768px)': {
                                    'fontSize': '12px'  # Smaller font size on mobile
                                }
                            }
                        ),

                        # Kelishsa bo'ladimi
                        html.Label("Kelishsa bo'ladimi", style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}),
                        dbc.RadioItems(
                            id='kelishsa-dropdown',
                            options=[
                                {'label': 'Ha', 'value': 'Yes'},
                                {'label': "Yo'q", 'value': 'No'}
                            ],
                            value='Yes',  # Set a default value
                            className="btn-group",
                            inputClassName="btn-check",
                            labelClassName="btn btn-outline-primary",
                            labelCheckedClassName="active",
                            style={'whiteSpace': 'nowrap', 'flexWrap': 'wrap'}  # Added flexWrap here as well
                        )
                    ]
                ),


                
                # #----komissiya bormi yo'qmi
                # html.Label('Komissiya bormi'),
                # dcc.Dropdown(
                #     id='komissiya-dropdown',
                #     options=[
                #         {'label': 'Ha', 'value': 'Yes'},
                #         {'label': "Yo'q", 'value': 'No'}
                #     ],
                #     placeholder="Komissiya bormi",
                #     style={'margin-bottom': '10px'}
                # ),
                #----oy
                html.Label(
            'Baholash oyi va yili', 
            style={'font-weight': 'bold', 'font-size': '18px', 'margin-top': '10px', 'margin-bottom': '5px'}
        ),
                html.Div([
                    #html.Label('Qurilgan oy'),
                    dcc.Input(
                        id='oy-input', 
                        type='number', 
                        placeholder='Qurilgan oyi', 
                        value=current_month,  
                        style={ 'width': '50%',  
                            'border-radius': '30px 0px 0px 30px',  # Makes edges rounded
                            'border': '1px solid #ccc',  # Optional: Adjust border color
                            'padding': '8px'}
                    ),
                    #html.Label('Yil'),
                    dcc.Input(
                        id='year-input', 
                        type='number', 
                        placeholder='Qurilgan yili', 
                        value=current_year,  
                        style={'width': '50%',  
                            'border-radius': '0px 30px 30px 0px',  # Makes edges rounded
                            'border': '1px solid #ccc',  # Optional: Adjust border color
                            'border-left': '0px',
                            'padding': '8px' })
                ], style={'display': 'flex', 'align-items': 'center'}),
            ]
        )
    ], xs=12, sm=12, md=6, lg=6, style={'padding': '10px'}),  
    
    
    dbc.Col([
        dbc.Row([
            # Details Card
            dbc.Card(
                [
                   dbc.CardBody(
                    [
                            html.Div([
                                html.Div([
                                    html.Span("Hudud: ", id='selected-hudud-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-hudud', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),
                                
                                html.Div([
                                    html.Span("Maydoni: ", id='selected-area-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-area', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Xonalar soni: ", id='selected-rooms-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-rooms', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Nechinchi qavat: ", id='selected-floor-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-floor', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Necha qavatli: ", id='selected-total-floors-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-total-floors', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Jihozlanganmi: ", style={'font-weight': 'bold'}),
                                    html.Span(id='selected-mebel', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Atrofda nimalar bor: ", style={'font-weight': 'bold'}),
                                    html.Span(id='selected-atrofda', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Uyda nimalar bor: ", style={'font-weight': 'bold'}),
                                    html.Span(id='selected-uyda', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Kim egalik qiladi: ", style={'font-weight': 'bold'}),
                                    html.Span(id='selected-owner', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Planirovka turi: ", id='selected-planirovka-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-planirovka', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Ta'mir turi: ", style={'font-weight': 'bold'}),
                                    html.Span(id='selected-renovation', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Sanuzel turi: ", id='selected-sanuzel-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-sanuzel', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Bozor turi: ", style={'font-weight': 'bold'}),
                                    html.Span(id='selected-bino-turi', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Qurilish turi: ", id='selected-qurilish-turi-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-qurilish-turi', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Kelishsa bo'ladimi: ", style={'font-weight': 'bold'}),
                                    html.Span(id='selected-kelishsa', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Baholash oyi va yili: ", style={'font-weight': 'bold'}),
                                    html.Span(id='selected-time', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),
                        html.Div(
                            id='time-display',
                            style={
                                        'position': 'relative',
                                        'margin-top': '10px',
                                        'text-align': 'right',
                                'font-size': '12px',
                                'color': 'black'
                                    }
                                ),
                                # Add Baholash button
                                html.Div([
                                    dbc.Button(
                                        'Baholash', 
                                        id='submit-button', 
                                        n_clicks=0, 
                                        style={
                                            'width': '200px',
                                            'background-color': '#00264D',
                                            'color': 'white',
                                            'border': 'none',
                                            'border-radius': '30px',
                                            'padding': '8px',
                                            'margin': '20px auto 0 auto'
                                        }
                                    )
                                ], style={
                                    'display': 'flex',
                                    'justify-content': 'center',
                                    'width': '100%',
                                    'margin-top': '20px'
                                }),
                            ], id='all-detail', style={
                                'white-space': 'pre-line',
                                'display': 'flex',
                                'flex-direction': 'column',
                                'gap': '5px',
                                'padding-bottom': '20px'
                            }),
                        ]
                    ),
                ], 
                className='custom-opensauce',
                   style={
                    'position': 'relative',
                    'width': '100%',
                    'border-radius': '10px',
                    'white-space': 'pre-line',
                    'height': 'fit-content',
                    'margin-top': '25px',
                    'padding': '20px'
                }
            ),

            # Price Card (moved below details card)
            dbc.Card([
                html.H4("Uyning baholangan bozor narxi", 
                       className='text-center mb-4',
                       style={'fontSize': '24px', 'fontWeight': 'normal', 'marginTop': '15px'}),
                html.Div([
                    dbc.Spinner(
                        html.Div([
                            html.H2(id='house-price',
                                   className='text-center',
                                   style={'fontSize': '48px', 'fontWeight': 'bold', 'marginBottom': '10px'}),
                            html.P(id='price-range',
                                  className='text-center',
                                  style={'fontSize': '16px', 'color': '#666'})
                        ]),
                        color="#00264D",
                        size="lg",
                        type="border"
                    )
                ], style={'minHeight': '150px', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
                dbc.Button(
                    "TO'LIQ HISOBOTNI YUKLAB OLISH",
                    id='download-button-home',
                    color="primary",
                    className="w-100 mt-3 mb-3",
                    style={
                        'width': '200px',
                        'backgroundColor': '#00264D',
                        'borderRadius': '30px',
                        'border': 'none',
                        'padding': '8px',
                        'margin': '20px auto',
                        'display': 'block'
                    }
                ),
                dcc.Download(id="download-pdf")
            
            
            
            
            
            
            
            ],
            className='mb-4',
            style={
                'border': '1px solid #ddd',
                'borderRadius': '15px',
                'padding': '20px',
                'marginTop': '20px',
                'backgroundColor': 'white'
            })
        ], style={'width': '100%', 'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}),
    ], xs=12, sm=12, md=6, lg=6, style={'padding': '10px'})
])



unique_reg_label = ['Toshkent shahri',
 'Qoraqalpogʻiston Respublikasi',
 'Navoiy Viloyati',
 'Toshkent Viloyati',
 'Samarqand Viloyati',
 'Qashqadaryo Viloyati',
 "Farg'ona Viloyati",
 'Buxoro Viloyati',
 'Xorazm Viloyati',
 'Sirdaryo Viloyati',
 'Surxondaryo Viloyati',
 'Namangan Viloyati',
 'Andijon Viloyati',
 'Jizzax Viloyati']
dropdown_viloyat = [{'label': label, 'value': label} for label in unique_reg_label]




#---- prediction tab Link Auto----#
prediction_auto = dbc.Row([
    dbc.Col([
        html.Div(
            id='auto-input-panel',
            className='custom-opensauce',
            style={
                'position': 'relative',
                'left': '0',
                'top': '50%',
                'transform': 'translateY(-50%)',
                'padding': '20px',
                'width': '100%',
                #'margin-top': '20px',
                'margin-bottom': '20px',
                'color': 'black',
                'font-weight': 'bold',
                'border': 'none'
            },            
            children=[


########################################################################################
                html.Label('Viloyatni tanlang', style={'display': 'block', 'font-weight': 'bold', 'margin-bottom': '5px'}),
                html.Div(
                    style={
                        'background-color': '#ffffff',
                        #'padding': '10px',
                        'border-radius': '30px',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        'display': 'flex',  # Makes items align in a row
                        #'gap': '10px'  # Adds space between the dropdowns
                    },
                    children=[
                        html.Div([
                            dcc.Dropdown(
                                id='auto-viloyat-dropdown',
                                options=dropdown_viloyat,
                                placeholder='Viloyatni tanlang',
                                style={
                                'width': '100%',  
                                'border-radius': '30px',  # Makes edges rounded
                                #'border': '1px solid #ccc',
                                #'padding': '8px'  # Optional: Adds spacing for better appearance
                                }
                            )
                        ], style={'flex': 1}),  # Makes both dropdowns take equal width
                    ]
                ),
################################################################################


                html.Label(
                'Brend nomi va Avtomobil nomi', 
                style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}
                ),
                html.Div(
                    style={
                        'background-color': '#ffffff',
                        'border-radius': '20px',
                        'display': 'flex',  # Places dropdowns next to each other
                    },
                    children=[
                        html.Div(
                            style={'width': '50%'},  # Each dropdown takes 50% of the width
                            children=[
                                dcc.Dropdown(
                                    id='auto-brend-dropdown', 
                                    options = [{'label':label, 'value':label} for label in brand_car_names.brand.unique().tolist()],
                                    placeholder='Brend nomi', 
                                    searchable=True,
                                    style={
                                        'width': '100%',  
                                        'border-radius': '30px 0px 0px 30px',  
                                        #'border': '1px solid #ccc',
                                        #'padding': '6px'
                                    }
                                ),
                            ]
                        ),
                        html.Div(
                            style={'width': '50%'},  
                            children=[
                                dcc.Dropdown(
                                    id='auto-name-dropdown', 
                                    #options=[{'label': f"{i} xona", 'value': i} for i in range(1, 11)],  # Room options from 1 to 10
                                    placeholder='Avtomobil nomi', 
                                    searchable=True,
                                    style={
                                        'width': '100%',  
                                        'border-radius': '0px 30px 30px 0px',
                                        #'border': '1px solid #ccc',
                                        #'padding': '6px'
                                    }
                                ),
                            ]
                        ),
                    ]
                ),



############################################################################################################
                html.Label(
        'Ishlab chiqarilgan yili va Motor hajmi', style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}
    ),

                html.Div(
                    style={
                        'background-color': '#ffffff',
                        #'padding': '15px',
                        'border-radius': '20px',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        'display': 'flex',  # Places inputs next to each other
                        #'gap': '10px',  # Adds space between them
                    },
                    children=[
                        dcc.Input(
                            id='auto-birth-input', 
                            type='number', 
                            placeholder='Ishlab chiqarilgan yili', 
                            value = 2020,
                            min=1980,
                            max=2025,
                            className='no-bold-placeholder',
                             style={
                            'width': '50%',  
                            'border-radius': '30px 0px 0px 30px',  # Makes edges rounded
                            'border': '1px solid #ccc', #'border': '1px solid #ccc',  # Optional: Adjust border color
                            'padding': '6px'  # Optional: Adds spacing for better appearance
                        }
                        ),
                        dcc.Input(
                            id='auto-motor-input', 
                            type='number', 
                            placeholder='Motor hajmi',
                            style={
                            'width': '50%',  
                            'border-radius': '0px 30px 30px 0px',
                            'border': '1px solid #ccc',
                            'padding': '6px'  # Optional: Adds spacing for better appearance
                        }
                        ),
                    ]
                ),

###############################################################################################################
            
                #----yaqin atrofda
                html.Label("Yoqilg'i turi", style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}),
                dcc.Dropdown(
                    id='auto-fuel-dropdown',
                    options=[
                        {'label':'Benzin','value':'Benzin'},
                        {'label':'Gaz/Benzin','value':'Gaz/Benzin'},
                        {'label':'Gibrid','value':'Gibrid'},
                        {'label':'Dizel','value':'Dizel'},
                        {'label':'Boshqa','value':'Boshqa'},
                        {'label':'Elektro','value':'Elektro'}
                    ],
                    multi=False,
                    placeholder="Yoqilg'i turi",
                    style={
                        'background-color': '#ffffff',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        #'padding': '10px',
                        'width': '100%',  # Make it full width
                        #'backgroundColor': '#f8f9fa',  # Light gray background
                        'border-radius': '30px',  # Rounded edges
                        #'border': '1px solid #ccc',  # Subtle border
                        #'fontSize': '16px'  # Bigger text
                        #'color': '#333'  # Darker text color
                    },
                ),

################################################################################################################

                #---- mebellimi yo'qmi
                html.Label('Egalik turi', style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}),
                dbc.RadioItems(
                    id='auto-owner-button',
                    options=[
                        {'label': 'Biznes', 'value': 'Biznes'},
                        {'label': "Xususiy", 'value': "Xususiy"},
                    ],
                    value='Xususiy',  # Default selected
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active"           
                ),
################################################################################################################              

                #----qurilish turi
                html.Label("Kuzov turi", style={'display': 'block', 'font-weight': 'bold', 'margin-bottom': '5px', 'margin-top': '10px'}),
                dcc.Dropdown(
                    id='auto-kuzov-dropdown',
                    # type='text',
                    options=[
                        {'label': 'Yo\'ltanlamas', 'value': 'Yo\'ltanlamas'},
                        {'label': 'Boshqa', 'value': 'Boshqa'},
                        {'label': 'Kabriolet', 'value': 'Kabriolet'},
                        {'label': 'Kupe', 'value': 'Kupe'},
                        {'label': 'Miniven', 'value': 'Miniven'},
                        {'label': 'Pikap', 'value': 'Pikap'},
                        {'label': 'Sedan', 'value': 'Sedan'},
                        {'label': 'Universal', 'value': 'Universal'},
                        {'label': 'Xetchbek', 'value': 'Xetchbek'}
                    ],
                    # value='Xetchbek',
                    placeholder='Kuzov turi',
                    className='no-bold-placeholder',
                    style={
                            'width': '100%',  
                            'border-radius': '30px',  # Makes edges rounded
                            'border': '1px solid #ccc', #'border': '1px solid #ccc',  # Optional: Adjust border color
                            'padding': '6px'  # Optional: Adds spacing for better appearance
                        }
                ),
                #  html.Label(
                #         'Kuzov turi', style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}
                #     ),

                # html.Div(
                #     style={
                #         'background-color': '#ffffff',
                #         #'padding': '15px',
                #         'border-radius': '20px',
                #         #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                #         'display': 'flex',  # Places inputs next to each other
                #         #'gap': '10px',  # Adds space between them
                #     },
                #     children=[
                #         dcc.Input(
                #             id='auto-kuzov-dropdown', 
                #             type='text', 
                #             min=1,
                #             max=4,
                #             step=1,
                #             placeholder='Kuzov turi', 
                #             className='no-bold-placeholder',
                #             value=1,
                #              style={
                #             'width': '100%',  
                #             'border-radius': '30px',  # Makes edges rounded
                #             'border': '1px solid #ccc', #'border': '1px solid #ccc',  # Optional: Adjust border color
                #             'padding': '6px'  # Optional: Adds spacing for better appearance
                #         }
                #         )
                #     ]
                # ),
                #---- planirovka turi
                html.Label('Avtomobil rangi', style={'display': 'block', 'font-weight': 'bold', 'margin-bottom': '5px', 'margin-top': '10px'}),
                dcc.Dropdown(
                    id='auto-color-dropdown',
                    options=[
                        {'label': 'Asfalt', 'value': 'Asfalt'},
                        {'label': 'Bejeviy', 'value': 'Bejeviy'},
                        {'label': 'Qora', 'value': 'Qora'},
                        {'label': "Ko'k", 'value': "Ko'k"},
                        {'label': "Jigarrang", 'value': 'Jigarrang'},
                        {'label': 'Kulrang', 'value': 'Kulrang'},
                        {'label': 'Kumush', 'value': 'Kumush'},
                        {'label': 'Oq', 'value': 'Oq'},
                        {'label': 'Boshqa', 'value': 'Boshqa'}


                    ],
                    placeholder='Avtomobil rangi',
                    style={
                        'background-color': '#ffffff',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        #'padding': '10px',
                        'width': '100%',  # Make it full width
                        #'backgroundColor': '#f8f9fa',  # Light gray background
                        'border-radius': '30px',  # Rounded edges
                        #'border': '1px solid #ccc',  # Subtle border
                        #'fontSize': '16px'  # Bigger text
                        #'color': '#333'  # Darker text color
                    },
                ),
                #---- sanuzel turi
                html.Label('Avtomobil holati', style={'display': 'block', 'font-weight': 'bold', 'margin-bottom': '5px', 'margin-top': '10px'}),
                dcc.Dropdown(
                    id='auto-condition-dropdown',
                    options=[
                        {'label': "A'lo", 'value': "A'lo"},
                        {'label': "O'rtacha", 'value': "O'rtacha"},
                        {'label':'Remont talab','value':'Remont talab'},
                        {'label':'Yaxshi','value':'Yaxshi'}
                    ],
                    placeholder='Avtomobil holati',
                    style={
                        'background-color': '#ffffff',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        #'padding': '10px',
                        'width': '100%',  # Make it full width
                        #'backgroundColor': '#f8f9fa',  # Light gray background
                        'border-radius': '30px',  # Rounded edges
                        #'border': '1px solid #ccc',  # Subtle border
                        #'fontSize': '16px'  # Bigger text
                        #'color': '#333'  # Darker text color
                    },
                ),
############################################################################
 #----uydagi jihozlar
                html.Label("Avtomobilning qo'shimcha narsalari", style={'display': 'block', 'font-weight': 'bold', 'margin-bottom': '5px', 'margin-top': '10px'}),
                dcc.Dropdown(
                    id='auto-feature-dropdown',
                    options=[
                        {'label': 'Konditsioner', 'value': 'Konditsioner'},
                        {'label': 'Xavfsizlik tizimi', 'value': 'Xavfsizlik tizimi'},
                        {'label': "Parctronik", 'value': "Parctronik"},
                        {'label': 'Rastamojka qilingan', 'value': 'Rastamojka qilingan',},
                        {'label': 'Elektron oynalar', 'value': 'Elektron oynalar'},
                        {'label': "Elektron ko'zgular", 'value': "Elektron ko'zgular"}
                    ],
                    multi=True,
                    placeholder="Avtomobilning qo'shimcha narsalari",
                    style={
                        'background-color': '#ffffff',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        #'padding': '10px',
                        'width': '100%',  # Make it full width
                        #'backgroundColor': '#f8f9fa',  # Light gray background
                        'border-radius': '30px',  # Rounded edges
                        #'border': '1px solid #ccc',  # Subtle border
                        #'fontSize': '16px'  # Bigger text
                        #'color': '#333'  # Darker text color
                    },
                ),                
############################################################################
                html.Label(
                        'Oldingi egalari soni', style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}
                    ),

                html.Div(
                    style={
                        'background-color': '#ffffff',
                        #'padding': '15px',
                        'border-radius': '20px',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        'display': 'flex',  # Places inputs next to each other
                        #'gap': '10px',  # Adds space between them
                    },
                    children=[
                        dcc.Input(
                            id='auto-ownerCount-input', 
                            type='number', 
                            min=1,
                            max=4,
                            step=1,
                            placeholder='Oldingi egalari soni', 
                            className='no-bold-placeholder',
                            value=1,
                             style={
                            'width': '100%',  
                            'border-radius': '30px',  # Makes edges rounded
                            'border': '1px solid #ccc', #'border': '1px solid #ccc',  # Optional: Adjust border color
                            'padding': '6px'  # Optional: Adds spacing for better appearance
                        }
                        )
                    ]
                ),

############################################################################## #               
                html.Label(
                        'Umumiy yurgan masofasi', style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}
                    ),

                html.Div(
                    style={
                        'background-color': '#ffffff',
                        #'padding': '15px',
                        'border-radius': '20px',
                        #'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                        'display': 'flex',  # Places inputs next to each other
                        #'gap': '10px',  # Adds space between them
                    },
                    children=[
                        dcc.Input(
                            id='auto-probeg-input', 
                            type='number', 
                            placeholder='Umumiy yurgan masofasi', 
                            className='no-bold-placeholder',
                             style={
                            'width': '100%',  
                            'border-radius': '30px 0px 0px 30px',  # Makes edges rounded
                            'border': '1px solid #ccc', #'border': '1px solid #ccc',  # Optional: Adjust border color
                            'padding': '6px'  # Optional: Adds spacing for better appearance
                        }
                        )
                    ]
                ),




################################################################################
                html.Div(
                    #style={'display': 'flex', 'flex-direction': 'column', 'gap': '20px'},
                    children=[
                        html.Div(
                            style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'flex-start'},
                            children=[
                                html.Label('Mexanik yoki Avtomat', style={'display': 'block', 'font-weight': 'bold', 'margin-top': '10px', 'margin-bottom': '5px'}),
                                html.Div(
                                    style={'display': 'flex', 'gap': '10px'},  # Make buttons horizontal
                                    children=[
                                        dbc.RadioItems(
                                            id='auto-transmission-button',
                                            options=[
                                                {'label': 'Mexanik', 'value': 'Mexanik'},
                                                {'label': "Avtomat", 'value': "Avtomat"}


                                            ],
                                            value='Mexanik',
                                            className="btn-group",
                                            inputClassName="btn-check",
                                            labelClassName="btn btn-outline-primary",
                                            labelCheckedClassName="active",
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),
                #----oy
                html.Label(
            'Baholash oyi va yili', 
            style={'font-weight': 'bold', 'font-size': '18px', 'margin-top': '10px', 'margin-bottom': '5px'}
        ),
                html.Div([
                    #html.Label('Qurilgan oy'),
                    dcc.Input(
                        id='auto-oy-input', 
                        type='number', 
                        placeholder='Qurilgan oyi', 
                        value=current_month,  
                        style={ 'width': '50%',  
                            'border-radius': '30px 0px 0px 30px',  # Makes edges rounded
                            'border': '1px solid #ccc',  # Optional: Adjust border color
                            'padding': '8px'}
                    ),
                    #html.Label('Yil'),
                    dcc.Input(
                        id='auto-year-input', 
                        type='number', 
                        placeholder='Qurilgan yili', 
                        value=current_year,  
                        style={'width': '50%',  
                            'border-radius': '0px 30px 30px 0px',  # Makes edges rounded
                            'border': '1px solid #ccc',  # Optional: Adjust border color
                            'border-left': '0px',
                            'padding': '8px' })
                ], style={'display': 'flex', 'align-items': 'center'}),
            ]
        )
    ], xs=12, sm=12, md=6, lg=6, style={'padding': '10px'}),  
    
    
   dbc.Col([
        dbc.Row([
            # Details Card
            dbc.Card(
                [
                   dbc.CardBody(
                    [
                            html.Div([
                                html.Div([
                                    html.Span("Hudud: ", id='selected-hudud-label', style={'font-weight': 'bold'}),
                                    html.Span(id='auto-selected-hudud', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),
                                
                                html.Div([
                                    html.Span("Brend nomi: ", id='selected-area-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-brend', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Avtomobil nomi: ", id='selected-rooms-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-name', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Ishlab chiqarilgan yili: ", id='selected-floor-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-birth', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Motor hajmi: ", id='selected-total-floors-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-motor', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Yoqilg'i turi: ", style={'font-weight': 'bold'}),
                                    html.Span(id='selected-fuel', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Egalik turi: ", style={'font-weight': 'bold'}),
                                    html.Span(id='selected-egalik', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Kuzov turi: ", style={'font-weight': 'bold'}),
                                    html.Span(id='selected-kuzov', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Avtomobil rangi: ", style={'font-weight': 'bold'}),
                                    html.Span(id='selected-color', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Avtomobil holati: ", id='selected-planirovka-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-condition', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Avtomobil alohida narsalari: ", style={'font-weight': 'bold'}),
                                    html.Span(id='selected-features', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Egalari soni: ", id='selected-sanuzel-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-ownerCount', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Umumiy yurgan masofasi: ", style={'font-weight': 'bold'}),
                                    html.Span(id='selected-probeg', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Mexanik yoki Avtomat: ", id='selected-qurilish-turi-label', style={'font-weight': 'bold'}),
                                    html.Span(id='selected-transmission', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),

                                html.Div([
                                    html.Span("Baholash oyi va yili: ", style={'font-weight': 'bold'}),
                                    html.Span(id='auto-selected-time', style={'margin-left': 'auto'})
                                ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}),
                        html.Div(
                            id='auto-time-display',
                            style={
                                        'position': 'relative',
                                        'margin-top': '10px',
                                        'text-align': 'right',
                                'font-size': '12px',
                                'color': 'black'
                                    }
                                ),
                                # Add Baholash button
                                html.Div([
                                    dbc.Button(
                                        'Baholash', 
                                        id='auto-submit-button', 
                                        n_clicks=0, 
                                        style={
                                            'width': '200px',
                                            'background-color': '#00264D',
                                            'color': 'white',
                                            'border': 'none',
                                            'border-radius': '30px',
                                            'padding': '8px',
                                            'margin': '20px auto 0 auto'
                                        }
                                    )
                                ], style={
                                    'display': 'flex',
                                    'justify-content': 'center',
                                    'width': '100%',
                                    'margin-top': '20px'
                                }),
                            ], id='all-detail', style={
                                'white-space': 'pre-line',
                                'display': 'flex',
                                'flex-direction': 'column',
                                'gap': '5px',
                                'padding-bottom': '20px'
                            }),
                        ]
                    ),
                ], 
                className='custom-opensauce',
                   style={
                    'position': 'relative',
                    'width': '100%',
                    'border-radius': '10px',
                    'white-space': 'pre-line',
                    'height': 'fit-content',
                    'margin-top': '25px',
                    'padding': '20px'
                }
            ),

            # Price Card (moved below details card)
            dbc.Card([
                html.H4("Avtomobilning baholangan bozor narxi", 
                       className='text-center mb-4',
                       style={'fontSize': '24px', 'fontWeight': 'normal', 'marginTop': '15px'}),
                html.Div([
                    dbc.Spinner(
                        html.Div([
                            html.H2(id='auto-price',
                                   className='text-center',
                                   style={'fontSize': '48px', 'fontWeight': 'bold', 'marginBottom': '10px'}),
                            html.P(id='auto-price-range',
                                  className='text-center',
                                  style={'fontSize': '16px', 'color': '#666'})
                        ]),
                        color="#00264D",
                        size="lg",
                        type="border"
                    )
                ], style={'minHeight': '150px', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
                dbc.Button(
                    "TO'LIQ HISOBOTNI YUKLAB OLISH",
                    id='download-button-auto',
                    color="primary",
                    className="w-100 mt-3 mb-3",
                    style={
                        'width': '200px',
                        'backgroundColor': '#00264D',
                        'borderRadius': '30px',
                        'border': 'none',
                        'padding': '8px',
                        'margin': '20px auto',
                        'display': 'block'
                    }
                ),
                dcc.Download(id="download-pdf-auto")
            ],
            className='mb-4',
            style={
                'border': '1px solid #ddd',
                'borderRadius': '15px',
                'padding': '20px',
                'marginTop': '20px',
                'backgroundColor': 'white'
            })
        ], style={'width': '100%', 'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}),
    ], xs=12, sm=12, md=6, lg=6, style={'padding': '10px'})
])


####################################################################################################
####################################################################################################

#---- overview tab Link Home----#
overview_home = dbc.Row([
    html.Div([
    html.Div([
        html.Iframe(
            src="https://app.powerbi.com/view?r=eyJrIjoiNWVhZmEwNjItYmE5NC00MjY1LTg2MGUtMGUyNmMxMmMzNWVlIiwidCI6ImI1OGVhYjJiLTA1YzYtNDcxYi1hYWRhLWNiNjMwY2MyMDJkYyIsImMiOjEwfQ%3D%3D" ,
                style={
                    'width': '100%',
                    'height': '85vh',
                    'border': 'none',
                    'borderRadius': '10px',
                    'backgroundColor': 'white'
                }
            )
        ], className='custom-opensauce', style={
            'maxWidth': '1200px',
            'margin': '0 auto',
            'padding': '40px',
            'backgroundColor': 'white',
            'borderRadius': '10px',
            'marginTop': '20px',
            'marginBottom': '40px'
        })
    ], style={
        'backgroundColor': 'white',
        'minHeight': '100vh',
        'padding': '20px',
        'width': '100%'
    })
])

#---- overview tab Link Auto----#

overview_auto = dbc.Row([
    html.Div([
    html.Div([
        html.Iframe(
                    src="https://app.powerbi.com/view?r=eyJrIjoiMWE0Y2Q4ZDItZWY2Yi00OTczLWFiMjgtYTkyYzQzZTNkYWMxIiwidCI6ImI1OGVhYjJiLTA1YzYtNDcxYi1hYWRhLWNiNjMwY2MyMDJkYyIsImMiOjEwfQ%3D%3D" ,
                    style={
                    'width': '100%',
                    'height': '85vh',
                    'border': 'none',
                    'borderRadius': '10px',
                    'backgroundColor': 'white'
                }


            )
        ], className='custom-opensauce', style={
            'maxWidth': '1200px',
            'margin': '0 auto',
            'padding': '40px',
            'backgroundColor': 'white',
            'borderRadius': '10px',
            'marginTop': '20px',
            'marginBottom': '40px'
        })
    ], style={
        'backgroundColor': 'white',
        'minHeight': '100vh',
        'padding': '20px',
        'width': '100%'
    })
])


####################################################################################################
####################################################################################################


#----app layout----#
app.layout = dbc.Container([
    #---- Link Data shapkasi----#
    dbc.Row([
        dbc.Col([
            html.Div([  # Added wrapper div for centering
            html.A(
            href='https://www.linkdata.uz',
            target='_blank',
            children=[
                html.Img(
                    src='/assets/logos_black.png',
                            style={'width': '200px'} #10px
                        )
                    ]
                )
            ], style={
                'maxWidth': '1400px',
                'margin': '0 auto',
                'paddingLeft': '40px',
                'paddingRight': '40px',
                'width': '100%'
            })
        ], width='auto', className='fixed-header', style={
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'right': 0,
            'background': 'white',
            'zIndex': 1000,
            'padding': '10px 0',  # Changed padding to only top/bottom
            'margin': 0,
            'width': '100%',
            'border': 'none'
        }),
        
        # Add a spacer div to prevent content from hiding behind the fixed header
        html.Div(style={'height': '80px'}),
    ], justify='left'),

    # Main product selection buttons
    dbc.Row([
    html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div(
                        dbc.Card([
                            html.H3("Link Home", className="text-center mb-2"),
                            html.P("Uylarni onlayn avtomatik baholash platformasi", className="text-center small")
                        ], 
                        id="link-home-button",
                        className="h-100 py-3",
                        style={
                            'backgroundColor': '#00264D',
                            'color': 'white',
                            'borderRadius': '10px',
                            'cursor': 'pointer',
                            'marginRight': '10px',
                            'transition': 'all 0.3s ease',
                            'border': 'none'
                        }),
                        id="link-home-container"
                    )
                ], width=6, className="h-100"),
                dbc.Col([
                    html.Div(
                        dbc.Card([
                            html.H3("Link Auto", className="text-center mb-2"),
                            html.P("Avtomobilni onlayn avtomatik baholash platformasi", className="text-center small")
                        ], 
                        id="link-auto-button",
                        className="h-100 py-3",
                        style={
                            'backgroundColor': 'white',
                            'color': '#00264D',
                            'border': '2px solid #00264D',
                            'borderRadius': '10px',
                            'cursor': 'pointer',
                            'marginLeft': '10px',
                            'transition': 'all 0.3s ease'
                        }),
                        id="link-auto-container"
                    )
                ], width=6, className="h-100"),
            ], className="mb-4", style={'maxWidth': '1200px', 'margin': '0 auto'})
        ], style={'padding': '20px'})
    ]),

    # Content area for selected product
    html.Div(id='product-content', children=[
        # Sub-tabs for Link Home
        html.Div([
            html.Div([
        dcc.Tabs(
            id='tabs-components',
                    value='prediction-tab',
            children=[
                dcc.Tab(
                    label='Baholash', 
                            value='prediction-tab',
                            className='custom-tab',
                            selected_className='custom-tab--selected'
                ),
                dcc.Tab(
                    label='Loyiha haqida', 
                            value='info-tab-home',
                            className='custom-tab',
                            selected_className='custom-tab--selected'
                ),
                dcc.Tab(
                    label='Bozor tahlili', 
                            value='overview-tab-home',
                            className='custom-tab',
                            selected_className='custom-tab--selected'
                        )
                    ]
                )
            ], className='tabs-wrapper'),
        html.Div(id='tabs-output')
        ], id='link-home-content'),
        
        # Content area for Link Auto (initially hidden)
        html.Div(id='link-auto-content', style={'display': 'none'}, children=[
            # Sub-tabs for Link Auto (same structure as Link Home)
            html.Div([
                html.Div([
                    dcc.Tabs(
                        id='tabs-components-auto',
                        value='prediction-tab-auto',
                        children=[
                            dcc.Tab(
                                label='Baholash', 
                                value='prediction-tab-auto',
                                className='custom-tab',
                                selected_className='custom-tab--selected'
                            ),
                            dcc.Tab(
                                label='Loyiha haqida', 
                                value='info-tab-auto',
                                className='custom-tab',
                                selected_className='custom-tab--selected'
                            ),
                            dcc.Tab(
                                label='Bozor tahlili', 
                                value='overview-tab-auto',
                                className='custom-tab',
                                selected_className='custom-tab--selected'
                            )
                        ]
                    )
                ], className='tabs-wrapper'),
                html.Div(id='tabs-output-auto')
            ])
        ])
    ])
], fluid=True, style={
    'backgroundColor': 'white', 
    'minHeight': '100vh', 
    'padding': '0',
    'margin': '0 auto',
    'maxWidth': '1400px',
    'paddingLeft': '20px',
    'paddingRight': '20px',
    'overflowX': 'hidden'
})


######### callbacks ########################################################################################################


#---- app callbacks ----#


@app.callback(
    Output('tabs-output', 'children'),
    Input('tabs-components', 'value')
)
def render_content(tab):
    if tab == 'prediction-tab':
        return prediction_home
    elif tab == 'overview-tab-home':
        return overview_home
    elif tab == 'info-tab-home':
        return info_tab_home
    return prediction_home  # Default to prediction if value is missing


######################### prediction tab callbacks ##########################################################################
##############################################################################################################################


#---- mahalla dropdown-----#
@app.callback(
    Output('mahalla-dropdown', 'options'),
    Input('district-dropdown', 'value')
)
def update_value_dropdown(selected_key):
    if selected_key is None:
        return []  # Return empty list if no district is selected
    
    # Filter the DataFrame
    filtered_df = mahalla_and_tuman[mahalla_and_tuman['district_str'] == selected_key]

    # Convert to dropdown format
    options = [{'label': name, 'value': name} for name in filtered_df['neighborhood_latin'].unique()]

    return options 



model_is=''
#----Link home callbacks----#
@app.callback(
    [Output('house-price', 'children'),
     Output('price-range', 'children'),
     Output('time-display', 'children'),
     Output('district-dropdown', 'style'),
     Output('mahalla-dropdown', 'style'),
     Output('area-input', 'style'),
     Output('rooms-input', 'style'),
     Output('floor-input', 'style'),
     Output('total-floors-input', 'style'),
     Output('qurilish-turi-dropdown', 'style'),
     Output('planirovka-dropdown', 'style'),
     Output('sanuzel-dropdown', 'style')],
    [Input('submit-button', 'n_clicks'),
     Input('district-dropdown', 'value'),
     Input('mahalla-dropdown', 'value'),
     Input('area-input', 'value'),
     Input('rooms-input', 'value'),
     Input('floor-input', 'value'),
     Input('total-floors-input', 'value'),
     Input('qurilish-turi-dropdown', 'value'),
     Input('planirovka-dropdown', 'value'),
     Input('sanuzel-dropdown', 'value')],
    [State('mebel-dropdown', 'value'),
    State('atrofda-dropdown', 'value'),
    State('uyda-dropdown', 'value'),
    State('owner-dropdown', 'value'),
    State('renovation-dropdown', 'value'),
    State('bino-turi-dropdown', 'value'),
    State('kelishsa-dropdown', 'value'),
    State('oy-input', 'value'),
     State('year-input', 'value')],
    prevent_initial_call=True
)
def predict_price(n_clicks, district, mahalla, area, rooms, floor, total_floors, qurilish_turi, planirovka, sanuzel,
                 mebel, atrofda, uyda, owner, renovation, bino_turi, kelishsa, month, year):
    ctx = callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Default styles for inputs
    default_left_dropdown_style = {
        'width': '100%',
        'border-radius': '30px 0px 0px 30px',
    }
    default_right_dropdown_style = {
        'width': '100%',
        'border-radius': '0px 30px 30px 0px',
        'border-left': '0px',
    }
    default_left_input_style = {
        'width': '100%',
        'border-radius': '30px 0px 0px 30px',
        'border': '1px solid #ccc',
        'padding': '6px'
    }
    default_right_input_style = {
        'width': '100%',
        'border-radius': '0px 30px 30px 0px',
        'border': '1px solid #ccc',
        'border-left': '0px',
        'padding': '6px'
    }
    default_single_dropdown_style = {
        'width': '100%',
        'border-radius': '30px',
    }

    error_left_dropdown_style = {
        'width': '100%',
        'border-radius': '30px 0px 0px 30px',
        'border': '1px solid #dc3545',
    }
    error_right_dropdown_style = {
        'width': '100%',
        'border-radius': '0px 30px 30px 0px',
        'border': '1px solid #dc3545',
        'border-left': '0px',
    }
    error_left_input_style = {
        'width': '100%',
        'border-radius': '30px 0px 0px 30px',
        'border': '1px solid #dc3545',
        'padding': '6px'
    }
    error_right_input_style = {
        'width': '100%',
        'border-radius': '0px 30px 30px 0px',
        'border': '1px solid #dc3545',
        'border-left': '0px',
        'padding': '6px'
    }
    error_single_dropdown_style = {
        'width': '100%',
        'border-radius': '30px',
        'border': '1px solid #dc3545',
    }

    # Initialize all styles as default
    styles = [
        default_left_dropdown_style.copy(),   # district
        default_right_dropdown_style.copy(),  # mahalla
        default_left_input_style.copy(),      # area
        default_right_input_style.copy(),     # rooms
        default_left_input_style.copy(),      # floor
        default_right_input_style.copy(),     # total_floors
        default_single_dropdown_style.copy(), # qurilish_turi
        default_single_dropdown_style.copy(), # planirovka
        default_single_dropdown_style.copy(), # sanuzel
    ]

    # If the callback was triggered by an input change (not the submit button), reset the display
    if trigger_id and trigger_id != 'submit-button':
        return (
            html.Div("Baholash tugmasini bosing", style={'fontSize': '22px'}),
            "",
            "",
            *styles
        )

    # Only proceed with prediction if the submit button was clicked
    if n_clicks > 0 and trigger_id == 'submit-button':
        # Add 3-second delay
        time.sleep(3)
        
        required_fields = {
            'hudud': (district is not None and mahalla is not None),
            'area': area is not None and area != '',
            'rooms': rooms is not None and rooms != '',
            'floor': floor is not None and floor != '',
            'total_floors': total_floors is not None and total_floors != '',
            'qurilish_turi': qurilish_turi is not None and qurilish_turi != '',
            'planirovka': planirovka is not None and planirovka != '',
            'sanuzel': sanuzel is not None and sanuzel != ''
        }
        
        # Update styles based on missing fields
        styles = [
            error_left_dropdown_style if not required_fields['hudud'] else default_left_dropdown_style.copy(),    # district
            error_right_dropdown_style if not required_fields['hudud'] else default_right_dropdown_style.copy(),  # mahalla
            error_left_input_style if not required_fields['area'] else default_left_input_style.copy(),          # area
            error_right_input_style if not required_fields['rooms'] else default_right_input_style.copy(),       # rooms
            error_left_input_style if not required_fields['floor'] else default_left_input_style.copy(),         # floor
            error_right_input_style if not required_fields['total_floors'] else default_right_input_style.copy(),# total_floors
            error_single_dropdown_style if not required_fields['qurilish_turi'] else default_single_dropdown_style.copy(), # qurilish_turi
            error_single_dropdown_style if not required_fields['planirovka'] else default_single_dropdown_style.copy(),    # planirovka
            error_single_dropdown_style if not required_fields['sanuzel'] else default_single_dropdown_style.copy(),       # sanuzel
        ]
        
        if not all(required_fields.values()):
            return (
                html.Div("Xatolik", style={'color': '#dc3545'}),  # Red error message
                html.Div("Iltimos kerakli ma'lumotlarni kiriting", style={'color': '#dc3545'}),  # Red error message
                "",
                *styles
            )

        updated_dict = my_dict3.copy()
        for key in updated_dict.keys():
            updated_dict[key] = 0

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update the dictionary with the inputs
        updated_dict["totalArea"] = area
        updated_dict["numberOfRooms"] = rooms
        updated_dict["floor"] = floor
        updated_dict["floorOfHouse"] = total_floors
        updated_dict["furnished"] = 1 if mebel == 'Ha' else 0

        if kelishsa == 'Ha':
            updated_dict['handle'] = 1
        else:
            updated_dict['handle'] = 0

        # Add in atrofda (multi-select)
        atrofda_keys = {
            "Maktab": "shkola",
            "Supermarket": "supermarket",
            "Do'kon": "magazini",
            "Avtoturargoh": "stoyanka",
            "Shifoxona": "bolnitsa",
            "Poliklinika": "poliklinika",
            "Bekat": "ostonovki",
            "Bolalar maydonchasi": "detskaya_ploshatka",
            "Restoran": "restorani",
            "Kafe": "kafe",
            "Ko'ngilochar maskanlar": "razvlekatelnie_zavedeniya",
            "Bog'cha": "detskiy_sad",
            "Yashil hudud": "zelyonaya_zona",
            "Park": "park"
        }
        
        if atrofda is not None:
            for key, item in atrofda_keys.items():
                updated_dict[item] = 1 if key in atrofda else 0
        else:
            for item in atrofda_keys.values():
                updated_dict[item] = 0

        # Add in uyda (multi-select)
        uyda_keys = {
            "Sovutgich": "tv_wm_ac_fridge",
            "Telefon": "telefon_internet",
            "Oshxona": "kuxniya",
            "Kabel TV": "kabelnoe_tv",
            "Internet": "telefon_internet",
            "Balkon": "balkon",
            "Kir yuvish mashinasi": "tv_wm_ac_fridge",
            "Konditsioner": "tv_wm_ac_fridge",
            "Televizor": "tv_wm_ac_fridge"
        }
        
        if uyda is not None:
            for key, item in uyda_keys.items():
                updated_dict[item] = 1 if key in uyda else 0
        else:
            for item in uyda_keys.values():
                updated_dict[item] = 0

        if mahalla in set(unique_mahalla_olx['neighborhood_code']):
            model = model1
            model_is = 'model1'
        else:
            model = model2
            model_is = 'model2'

        if district:
            filtered_values = mahalla_and_tuman.loc[mahalla_and_tuman['district_str'] == district, 'district_code']
            updated_dict['district_code'] = next(iter(filtered_values), None)

        if mahalla:
            filtered_values = mahalla_and_tuman.loc[mahalla_and_tuman['neighborhood_latin'] == mahalla, 'neighborhood_code']
            updated_dict['neighborhood_code'] = next(iter(filtered_values), None)

        if owner:
            updated_dict[f"ownerType_{owner}"] = 1
        if planirovka:
            updated_dict[f"planType_{planirovka}"] = 1
        if renovation:
            updated_dict[f"repairType_{renovation}"] = 1
        if sanuzel:
            updated_dict[f"bathroomType_{sanuzel}"] = 1
        if bino_turi:
            updated_dict[f"marketType_{bino_turi}"] = 1
        if qurilish_turi:
            updated_dict[f"buildType_{qurilish_turi}"] = 1
        
        updated_dict["pricingMonth"] = month if month is not None else current_month
        updated_dict["pricingYear"] = year if year is not None else current_year

        df_gathrd = pd.DataFrame([updated_dict])
        if model_is == 'model1':
            df_gathrd = df_gathrd
        else:
            df_gathrd = df_gathrd[uybor_cols['Unnamed: 0'].tolist()]
        
        prediction = model.predict(df_gathrd)
        predicted_price = round(prediction[0])
        margin = round(prediction[0] * 0.0361)
        lower_bound = predicted_price - margin
        upper_bound = predicted_price + margin

        # Reset styles to default after successful prediction
        default_styles = [
            default_left_dropdown_style.copy(),   # district
            default_right_dropdown_style.copy(),  # mahalla
            default_left_input_style.copy(),      # area
            default_right_input_style.copy(),     # rooms
            default_left_input_style.copy(),      # floor
            default_right_input_style.copy(),     # total_floors
            default_single_dropdown_style.copy(), # qurilish_turi
            default_single_dropdown_style.copy(), # planirovka
            default_single_dropdown_style.copy(), # sanuzel
        ]

        # After successful prediction, update the counter
        if predicted_price != '':
            try:
                events = load_prediction_counts()
                new_event = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'home': 1,
                    'auto': 0,
                    'home_downloads': 0,
                    'auto_downloads': 0
                }
                events.append(new_event)
                save_prediction_counts(events)
                print(f"\n[Link Home] New prediction event recorded at {new_event['timestamp']}")
            except Exception as e:
                print(f"Error recording prediction event: {str(e)}")
        
        return (
            f"${predicted_price:,}",
            f"${lower_bound:,} - ${upper_bound:,} orasida baholanishi mumkin",
            current_time,
            *default_styles
        )

    # Default return with initial styles
    return (
        html.Div("Baholash tugmasini bosing", style={'fontSize': '22px'}),
        "",
        "",
        *styles
    )

@app.callback(
    Output('total-floors-input', 'min'),
    Input('floor-input', 'value'),
)
def update_min_total_floors(floor_value):
    # Ensure the total floors input minimum value is at least the floor number
    if floor_value is not None:
        return floor_value
    # Default min value when no floor value is provided
    return 1

@app.callback(
    Output('selected-hudud', 'children'),
    [Input('district-dropdown', 'value'),
     Input('mahalla-dropdown', 'value')]
)
def update_hudud(district, mahalla):
    if district and mahalla:
        return f"{district}, {mahalla}"
    elif district:
        return district
    return ""

@app.callback(
    Output('selected-area', 'children'),
    [Input('area-input', 'value')]
)
def update_area(area):
    if area:
        return f"{area}m²"
    return ""

@app.callback(
    Output('selected-rooms', 'children'),
    [Input('rooms-input', 'value')]
)
def update_rooms(rooms):
    if rooms:
        return str(rooms)
    return ""

@app.callback(
    Output('selected-floor', 'children'),
    [Input('floor-input', 'value')]
)
def update_floor(floor):
    if floor:
        return str(floor)
    return ""

@app.callback(
    Output('selected-total-floors', 'children'),
    [Input('total-floors-input', 'value')]
)
def update_total_floors(total_floors):
    if total_floors:
        return str(total_floors)
    return ""

@app.callback(
    Output('selected-mebel', 'children'),
    [Input('mebel-dropdown', 'value')]
)
def update_mebel(mebel):
    if mebel:
        return str(mebel)
    return ""

@app.callback(
    Output('selected-atrofda', 'children'),
    [Input('atrofda-dropdown', 'value')]
)
def update_atrofda(atrofda):
    if atrofda:
        return ", ".join(atrofda)
    return ""

@app.callback(
    Output('selected-uyda', 'children'),
    [Input('uyda-dropdown', 'value')]
)
def update_uyda(uyda):
    if uyda:
        return ", ".join(uyda)
    return ""

@app.callback(
    Output('selected-owner', 'children'),
    [Input('owner-dropdown', 'value')]
)
def update_owner(owner):
    if owner:
        return str(owner)
    return ""

@app.callback(
    Output('selected-planirovka', 'children'),
    [Input('planirovka-dropdown', 'value')]
)
def update_planirovka(planirovka):
    planirovka_labels = {
        'Alohida_ajratilgan': 'Alohida ajratilgan',
        'Aralash': 'Aralash',
        'Aralash_alohida': 'Aralash alohida',
        'Kichik_oilalar_uchun': 'Kichik oilalar uchun',
        'Ko_p_darajali': 'Ko\'p darajali',
        'Pentxaus': 'Pentxaus',
        'Studiya': 'Studiya'
    }
    if planirovka:
        return planirovka_labels.get(planirovka, planirovka)
    return ""

@app.callback(
    Output('selected-renovation', 'children'),
    [Input('renovation-dropdown', 'value')]
)
def update_renovation(renovation):
    if renovation:
        return str(renovation)
    return ""

@app.callback(
    Output('selected-sanuzel', 'children'),
    [Input('sanuzel-dropdown', 'value')]
)
def update_sanuzel(sanuzel):
    sanuzel_labels = {
        '2_va_undan_ko_p_sanuzel': '2 va undan ko\'p sanuzel',
        'Alohida': 'Alohida',
        'Aralash': 'Aralash'
    }
    if sanuzel:
        return sanuzel_labels.get(sanuzel, sanuzel)
    return ""

@app.callback(
    Output('selected-bino-turi', 'children'),
    [Input('bino-turi-dropdown', 'value')]
)
def update_bino_turi(bino_turi):
    bino_turi_labels = {
        'Ikkilamchi_bozor': 'Ikkilamchi bozor',
        'Yangi_qurilgan_uylar': 'Yangi qurilgan'
    }
    if bino_turi:
        return bino_turi_labels.get(bino_turi, bino_turi)
    return ""

@app.callback(
    Output('selected-qurilish-turi', 'children'),
    [Input('qurilish-turi-dropdown', 'value')]
)
def update_qurilish_turi(qurilish_turi):
    qurilish_turi_labels = {
        'Blokli': 'Blokli',
        'G_ishtli': 'G\'ishtli',
        'Monolitli': 'Monolitli',
        'Panelli': 'Panelli',
        'Yog_ochli': 'Yog\'ochli'
    }
    if qurilish_turi:
        return qurilish_turi_labels.get(qurilish_turi, qurilish_turi)
    return ""

@app.callback(
    Output('selected-kelishsa', 'children'),
    [Input('kelishsa-dropdown', 'value')]
)
def update_kelishsa(kelishsa):
    kelishsa_labels = {
        'Yes': 'Ha',
        'No': 'Yo\'q'
    }
    if kelishsa:
        return kelishsa_labels.get(kelishsa, kelishsa)
    return ""

@app.callback(
    Output('selected-time', 'children'),
    [Input('oy-input', 'value'),
     Input('year-input', 'value')]
)
def update_time(month, year):
    if month and year:
        return f"{month}-{year}"
    return ""
####################################Link Home######################################################################

@app.callback(
    Output('download-button-home', 'disabled'),
    [Input('house-price', 'children')]
)
def toggle_download_button(price):
    if price and price != "Baholash tugmasini bosing" and not isinstance(price, dict):
        return False
    return True
@app.callback(
    Output("download-pdf", "data"),
    Input("download-button-home", "n_clicks"),
    [State('selected-hudud', 'children'),
     State('selected-area', 'children'),
     State('selected-rooms', 'children'),
     State('selected-floor', 'children'),
     State('selected-total-floors', 'children'),
     State('selected-mebel', 'children'),
     State('selected-atrofda', 'children'),
     State('selected-uyda', 'children'),
     State('selected-owner', 'children'),
     State('selected-planirovka', 'children'),
     State('selected-renovation', 'children'),
     State('selected-sanuzel', 'children'),
     State('selected-bino-turi', 'children'),
     State('selected-qurilish-turi', 'children'),
     State('selected-kelishsa', 'children'),
     State('selected-time', 'children'),
     State('house-price', 'children'),
     State('price-range', 'children')],
    prevent_initial_call=True
)
def generate_pdf(n_clicks, hudud, area, rooms, floor, total_floors, mebel, atrofda, uyda, 
                owner, planirovka, renovation, sanuzel, bino_turi, qurilish_turi, kelishsa, 
                time_value, price, price_range):
    if not n_clicks:
        return no_update
        
    # Create a dictionary of property details
    property_details = {
        'Hudud': hudud,
        'Maydoni': area,
        'Xonalar soni': rooms,
        'Qavat': floor,
        'Binoning qavatlar soni': total_floors,
        'Jihozlangan': mebel,
        'Atrofda': atrofda,
        'Uyda mavjud': uyda,
        'Mulk turi': owner,
        'Planirovka': planirovka,
        "Ta'mir turi": renovation,
        'Sanuzel': sanuzel,
        'Bozor turi': bino_turi,
        'Qurilish turi': qurilish_turi,
        "Kelishish mumkinmi": kelishsa,
        'Baholash vaqti': time_value
    }
    
    # Generate PDF
    try:
        pdf_bytes = create_report(property_details, price.replace('$', '').replace(',', ''), price_range)

        # Record download event
        try:
            events = load_prediction_counts()
            new_event = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'home': 0,
                'auto': 0,
                'home_downloads': 1,
                'auto_downloads': 0
            }
            events.append(new_event)
            save_prediction_counts(events)
            print(f"\n[Link Home] New download event recorded at {new_event['timestamp']}")
        except Exception as e:
            print(f"Error recording download event: {str(e)}")
        
        return dcc.send_bytes(pdf_bytes, f"linkhome_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return no_update

@app.callback(
    [Output('link-home-content', 'style'),
     Output('link-auto-content', 'style'),
     Output('link-home-button', 'style'),
     Output('link-auto-button', 'style')],
    [Input('link-home-container', 'n_clicks'),
     Input('link-auto-container', 'n_clicks')]
)
def switch_product(home_clicks, auto_clicks):
    ctx = callback_context
    if not ctx.triggered:
        # Default state (Link Home active)
        return {'display': 'block'}, {'display': 'none'}, {
            'backgroundColor': '#00264D',
            'color': 'white',
            'borderRadius': '10px',
            'border': 'none',
            'cursor': 'pointer',
            'marginRight': '10px',
            'transition': 'all 0.3s ease'
        }, {
            'backgroundColor': 'white',
            'color': '#00264D',
            'border': '2px solid #00264D',
            'borderRadius': '10px',
            'cursor': 'pointer',
            'marginLeft': '10px',
            'transition': 'all 0.3s ease'
        }
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'link-auto-container':
        return {'display': 'none'}, {'display': 'block'}, {
            'backgroundColor': 'white',
            'color': '#00264D',
            'border': '2px solid #00264D',
            'borderRadius': '10px',
            'cursor': 'pointer',
            'marginRight': '10px',
            'transition': 'all 0.3s ease'
        }, {
            'backgroundColor': '#00264D',
            'color': 'white',
            'borderRadius': '10px',
            'border': 'none',
            'cursor': 'pointer',
            'marginLeft': '10px',
            'transition': 'all 0.3s ease'
        }
    
    return {'display': 'block'}, {'display': 'none'}, {
        'backgroundColor': '#00264D',
        'color': 'white',
        'borderRadius': '10px',
        'border': 'none',
        'cursor': 'pointer',
        'marginRight': '10px',
        'transition': 'all 0.3s ease'
    }, {
        'backgroundColor': 'white',
        'color': '#00264D',
        'border': '2px solid #00264D',
        'borderRadius': '10px',
        'cursor': 'pointer',
        'marginLeft': '10px',
        'transition': 'all 0.3s ease'
    }

@app.callback(
    Output('tabs-output-auto', 'children'),
    Input('tabs-components-auto', 'value')
)
def render_content_auto(tab):
    if tab == 'prediction-tab-auto':
        return prediction_auto
    elif tab == 'overview-tab-auto':
        return overview_auto
    elif tab == 'info-tab-auto':
        return info_tab_auto
    return prediction_auto  # Default to prediction if value is missing








@app.callback(
    Output('auto-name-dropdown', 'options'),
    Input('auto-brend-dropdown', 'value')
)

def update_car_options(brand_type):
    names = brand_car_names[brand_car_names['brand'] == brand_type]['car_name'].unique().tolist()
    dropdown_car_names = [{'label': str(label).replace('_', ' '), 'value': label} for label in names]
    return dropdown_car_names


@app.callback(
    Output('auto-kuzov-dropdown', 'value'),  # dcc.Input expects a string
    Output('auto-motor-input', 'value'),
    Input('auto-name-dropdown', 'value')
)
def update_kuzov_motor(selected_key):
    if selected_key is None:
        return "", None  # Use an empty string for input fields

    filtered_df = car_body_enginevol[car_body_enginevol['car_name'] == selected_key]

    if filtered_df.empty:
        return "", None  # Return empty values if no match found

    car_body = filtered_df.iloc[0]['body_type']  # Assign the correct string
    engine_vol = filtered_df.iloc[0]['engine_volume'] if not pd.isnull(filtered_df.iloc[0]['engine_volume']) else None

    return car_body, engine_vol

#----Link  auto callbacks----#
@app.callback(
    [Output('auto-price', 'children'),
     Output('auto-price-range', 'children'),
     Output('auto-time-display', 'children'),
     Output('auto-viloyat-dropdown', 'style'),
     Output('auto-brend-dropdown', 'style'),
     Output('auto-name-dropdown', 'style'),
     Output('auto-birth-input', 'style'),
     Output('auto-motor-input','style'),
     Output('auto-fuel-dropdown','style'),
     Output('auto-kuzov-dropdown', 'style'),
     Output('auto-color-dropdown', 'style'),
     Output('auto-condition-dropdown', 'style'),
     Output('auto-ownerCount-input', 'style'),
     Output('auto-probeg-input', 'style')
     #Output('auto-transmission-button', 'style'),
                   # ← Add this if used
     
     ],
    [Input('auto-submit-button', 'n_clicks'),
     Input('auto-viloyat-dropdown', 'value'),
     Input('auto-brend-dropdown', 'value'),
     Input('auto-name-dropdown', 'value'),
     Input('auto-birth-input', 'value'),
     Input('auto-motor-input', 'value'),
     Input('auto-fuel-dropdown', 'value'),
     Input('auto-owner-button', 'value'),
     Input('auto-kuzov-dropdown', 'value')],
    [State('auto-color-dropdown', 'value'),
     State('auto-condition-dropdown', 'value'),
     State('auto-feature-dropdown', 'value'),
     State('auto-ownerCount-input', 'value'),
     State('auto-probeg-input', 'value'),
     State('auto-transmission-button', 'value'),
     State('auto-oy-input', 'value'),
     State('auto-year-input', 'value')],
    prevent_initial_call=True
)

def predict_auto_price(n_clicks, viloyat, brend, name, birth, motor, fuel, egalik, kuzov,
                 color, condition, feature, ownerCount, probeg, mexan_avto, month, year):
    ctx = callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    print(trigger_id)
    
    # Default styles for inputs
 
   
    
      
  

    
######################################################################
    default_styles_full_dropdown = {'width': '100%',  
                                'border-radius': '30px',}
    default_styles_left_dropdown = {
        'width': '100%',  
        'border-radius': '30px 0px 0px 30px',
    }
    default_styles_right_dropdown = {
        'width': '100%',  
        'border-radius': '0px 30px 30px 0px',
    }
    default_styles_left_input = {
        'width': '50%',  
        'border-radius': '30px 0px 0px 30px',  # Makes edges rounded
        'border': '1px solid #ccc', #'border': '1px solid #ccc',  # Optional: Adjust border color
        'padding': '6px'
    }
    default_styles_right_input = {
                            'width': '50%',  
                            'border-radius': '0px 30px 30px 0px',
                            'border': '1px solid #ccc',
                            'padding': '6px'
    }
    default_styles_single_input = {
                            'width': '100%',  
                            'border-radius': '30px',  # Makes edges rounded
                            'border': '1px solid #ccc', #'border': '1px solid #ccc',  # Optional: Adjust border color
                            'padding': '6px'
    }
##########################################################################
    # error_style = {'border': '1px solid #dc3545'}
    error_style_viloyat = {'border': '1px solid #dc3545', 'border-radius': '30px'}

    error_style_brend = {'border': '1px solid #dc3545','width':'100%','height':'37px', 'border-radius': '30px 0px 0px 30px'}
    error_style_name = {'border': '1px solid #dc3545','width':'100%','height':'37px', 'border-radius': '0px 30px 30px 0px'}
    error_style_ownerCount = {'border': '2px solid #dc3545','width':'100%','height':'37px','border-radius': '30px'}
    # error_style_kuzov = {'border': '20px solid #dc3545','width':'100%','height':'37px','border-radius': '30px'}

    # Initialize all styles as default
    styles = [
        default_styles_full_dropdown.copy(),   # viloyat
        default_styles_left_dropdown.copy(),      # brend
        default_styles_right_dropdown.copy(),  # name
        default_styles_left_input.copy(),     # birth
        default_styles_right_input.copy(),     #motor
        default_styles_full_dropdown.copy(), # fuel
        default_styles_full_dropdown.copy(), # kuzov
        default_styles_full_dropdown.copy(), # color                
        default_styles_full_dropdown.copy(), # condition
        default_styles_single_input.copy(), # ownerCount
        default_styles_single_input.copy(), # probeg
    ]
    
    # If the callback was triggered by an input change (not the submit button), reset the display
    if trigger_id and trigger_id != 'auto-submit-button':
        return (
            html.Div("Baholash tugmasini bosing", style={'fontSize': '22px'}),
            "",
            "",
            *styles
        )

    # Only proceed with prediction if the submit button was clicked
    if n_clicks > 0 and trigger_id == 'auto-submit-button':
        # Add 3-second delay
        time.sleep(3)

        required_fields = {
            'viloyat': viloyat is not None and viloyat != '',
            'brend': brend is not None and brend != '',
            'name': name is not None and name != '',
            'birth': birth is not None and birth != '',
            'motor': motor is not None and motor != '',
            'fuel': fuel is not None and fuel != '',
            'kuzov': kuzov is not None and kuzov != '',
            'probeg': probeg is not None and probeg != '',
            'color': color is not None and color != '',
            'ownerCount': ownerCount is not None and ownerCount != '',
            'condition': condition is not None and condition != ''
        }
        
        # Update styles based on missing fields
        error_styles = [
            error_style_viloyat if not required_fields['viloyat'] else default_styles_full_dropdown.copy(),    # viloyat
            error_style_brend if not required_fields['brend'] else default_styles_left_dropdown.copy(),    # brend
            error_style_name if not required_fields['name'] else default_styles_right_dropdown.copy(),            # name
            error_style_brend if not required_fields['birth'] else default_styles_left_input.copy(),         # birth,
            error_style_name if not required_fields['motor'] else default_styles_right_input.copy(),         # motor
            error_style_viloyat if not required_fields['fuel'] else default_styles_full_dropdown.copy(),   # fuel
            error_style_ownerCount if not required_fields['kuzov'] else default_styles_single_input.copy(),  # ownerCount
            error_style_viloyat if not required_fields['color'] else default_styles_full_dropdown.copy(),   # color
            error_style_viloyat if not required_fields['condition'] else default_styles_full_dropdown.copy(),   # condition
            error_style_ownerCount if not required_fields['ownerCount'] else default_styles_single_input.copy(),  # ownerCount
            error_style_ownerCount if not required_fields['probeg'] else default_styles_single_input.copy(),   # probeg
        ]
        
        if not all(required_fields.values()):
            return (
                html.Div("Xatolik", style={'color': '#dc3545'}),  # Red error message
                html.Div("Iltimos kerakli ma'lumotlarni kiriting", style={'color': '#dc3545'}),  # Red error message
                "",
                *error_styles
            )

        # Prepare data for prediction
        if brend in ['Chevrolet', 'Ravon', 'Daewoo']:
            updated_auto_dict = my_dict1.copy()
            for key in updated_auto_dict.keys():
                updated_auto_dict[key] = 0
            model = model3
            scaler = scaler1
            check = 'model_3'
        else:
            updated_auto_dict = my_dict2.copy()
            model = model4
            scaler = scaler2
            check = 'model_4'


        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update color features
        car_color_keys = {
            "Asfalt": "Asphalt",
            "Bejeviy": "Beige",
            "Qora": "Black",
            "Ko'k": "Blue",
            "Jigarrang": "Brown",
            "Kulrang": "Gray",
            "Boshqa": "Other",
            "Kumush": "Silver",
            "Oq": "White"
        }
        
        if color is not None:
            for key, color in car_color_keys.items():
                updated_auto_dict[f'color_{color}']=1 if key in color else 0

        # Update brand type
        if brend == 'Chevrolet':
            updated_auto_dict['brand_type'] = 1
        else:
            updated_auto_dict['brand_type'] = 0
        
        # Update car name
        if name:
            updated_auto_dict[f'car_name_{name}'] = 1

        updated_auto_dict["release_year"] = birth if birth is not None else 0
    
        # Update the dictionary with the inputs
        updated_auto_dict["engine_volume"] = motor if motor is not None else 0
      

        # if kelishsa == 'Ha':
        #     updated_auto_dict['handle'] = 1
        # else:
        #     updated_auto_dict['handle'] = 0

        # Add in condition (multi-select)
        car_condition_keys = {
            "A'lo": "Excellent",
            "O'rtacha": "Average",
            "Remont talab": "Needs_Repair",
            "Yaxshi": "Good"
        }
        
        if condition is not None:
            for key, value in car_condition_keys.items():
                updated_auto_dict[f'car_condition_{value}'] = 1 if key in condition else 0

        # Update feature flags
        car_feature_keys = {
            "Konditsioner": "Air_Conditioner",
            "Xavfsizlik tizimi": "Security_System",
            "Parctronik": "Parking_Sensors",
            "Rastamojka qilingan": "Customs_Cleared",
            "Elektron oynalar": "Power_Windows",
            "Elektron ko'zgular": "Power_Mirrors"
        }
        
        if feature is not None:
            for key, item in car_feature_keys.items():
                updated_auto_dict[item] = 1 if key in feature else 0
        else:
            for item in car_feature_keys.values():
                updated_auto_dict[item] = 0  # Default to 0 if None

        # if mahalla in set(unique_mahalla_olx['neighborhood_code']):
        #     model = model1
        #     model_is = 'model1'
        # else:
        #     model = model2
        #     model_is = 'model2'
        unique_reg_dict = {
            "Toshkent shahri": "Tashkent",
            "Qoraqalpogʻiston Respublikasi": "Karakalpakstan",
            "Navoiy Viloyati": "Navoiy",
            "Toshkent Viloyati": "Tashkent2",
            "Samarqand Viloyati": "Samarkand",
            "Qashqadaryo Viloyati": "Kashkadarya",
            "Farg'ona Viloyati": "Ferghana",
            "Buxoro Viloyati": "Bukhara",
            "Xorazm Viloyati": "Khorezm",
            "Sirdaryo Viloyati": "Sirdaryo",
            "Surxondaryo Viloyati": "Surkhondaryo",
            "Namangan Viloyati": "Namangan",
            "Andijon Viloyati": "Andijon",
            "Jizzax Viloyati": "Jizzakh"
        }
        
        if viloyat is not None:
            for key, viloyat in unique_reg_dict.items():
                updated_auto_dict[f"state_{viloyat}"] = 1 if key in viloyat else 0
       
        if ownerCount:
            updated_auto_dict[f'owners_count_{ownerCount}']=1

        # Update ownership type
        if egalik == 'Biznes':
            updated_auto_dict['item_type_Business'] = 1
            updated_auto_dict['item_type_Private'] = 0
        else:
            updated_auto_dict['item_type_Business'] = 0
            updated_auto_dict['item_type_Private'] = 1

        # Update mileage
        updated_auto_dict["mileage"] = probeg if probeg is not None else 0

        # Update body type
        car_type_dict = {
            "Yo'ltanlamas": "SUV",
            "Boshqa": "Other",
            "Kabriolet": "Convertible",
            "Kupe": "Coupe",
            "Miniven": "Minivan",
            "Pikap": "Pickup",
            "Sedan": "Sedan",
            "Universal": "Wagon",
            "Xetchbek": "Hatchback"
        }
        
        if kuzov is not None:
            for key, kuzov in car_type_dict.items():
                updated_auto_dict[f"body_{kuzov}"] = 1 if key in kuzov else 0

        # Update transmission
        if mexan_avto == 'Mexanik':
            updated_auto_dict['transmission'] = 1
        else:
            updated_auto_dict['transmission'] = 0
        # Update fuel type
        car_fuel_keys ={
            "Benzin": "Gasoline",
            "Gaz/Benzin": "Gasoline/Petrol",
            "Gibrid": "Hybrid",
            "Dizel": "Diesel",
            "Boshqa": "Other",
            "Elektro": "Electric"
        }

        if fuel is not None:
            for key, fuel in car_fuel_keys.items():
                updated_auto_dict[f"fuel_type_{fuel}"] = 1 if key in fuel else 0
     
        # Update time features
        updated_auto_dict["month"] = month if month is not None else 1
        updated_auto_dict["year"] = year if year is not None else 2025

        df_auto = pd.DataFrame([updated_auto_dict])
        print(check)
        if check == "model_4":
            # Remove specific columns from df_auto
            df_auto = df_auto.drop(columns=["body_Convertible", "color_Beige"], errors="ignore")
        elif check == "model_3":
            df_auto = df_auto.drop(columns=["color_Beige"], errors="ignore")
            

        #df_auto.to_csv('dfgathrd_link_auto.csv')  # Show the first few rows
        df_auto = scaler.transform(df_auto)
        prediction = model.predict(df_auto)
        predicted_price = round(prediction[0])
        margin = round(prediction[0] * 0.0361)
        lower_bound = predicted_price - margin
        upper_bound = predicted_price + margin
        
        # Format the prediction and range
        #formatted_prediction = f"{prediction:,.0f}"
        #formatted_range = f"{lower_bound:,.0f} - {upper_bound:,.0f}"

        # Reset styles to default after successful prediction
        default_styles = [
            default_styles_full_dropdown.copy(),   # viloyat
            default_styles_left_dropdown.copy(),      # brend
            default_styles_right_dropdown.copy(),  # name
            default_styles_left_input.copy(),     # birth
            default_styles_right_input.copy(),     #motor
            default_styles_full_dropdown.copy(), # fuel
            default_styles_full_dropdown.copy(), # kuzov
            default_styles_full_dropdown.copy(), # color                
            default_styles_full_dropdown.copy(), # condition
            default_styles_single_input.copy(), # ownerCount
            default_styles_single_input.copy(), # probeg
        ]

        # After successful prediction, update the counter
        if predicted_price != '':
            try:
                events = load_prediction_counts()
                new_event = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'home': 0,
                    'auto': 1,
                    'home_downloads': 0,
                    'auto_downloads': 0
                }
                events.append(new_event)
                save_prediction_counts(events)
                print(f"\n[Link Auto] New prediction event recorded at {new_event['timestamp']}")
            except Exception as e:
                print(f"Error recording prediction event: {str(e)}")
        
        return (
            f"${predicted_price:,}",
            f"${lower_bound:,} - ${upper_bound:,} orasida baholanishi mumkin",
            current_time,
            *default_styles
        )

    # Default return with initial styles
    return (
        html.Div("Baholash tugmasini bosing", style={'fontSize': '22px'}),
        "",
        "",
        *styles
    )



@app.callback(
    Output('auto-selected-hudud', 'children'),
    [Input('auto-viloyat-dropdown', 'value')]
)
def hudud(viloyat):
    if viloyat:
        return str(viloyat)
    return ""

@app.callback(
    Output('selected-brend', 'children'),
    [Input('auto-brend-dropdown', 'value')]
)
def update_brend(brend):
    if brend:
        return f"{brend}"
    return ""

@app.callback(
    Output('selected-name', 'children'),
    [Input('auto-name-dropdown', 'value')]
)
def update_name(name):
    if name:
        return str(name)
    return ""

@app.callback(
    Output('selected-birth', 'children'),
    [Input('auto-birth-input', 'value')]
)
def update_birth(birth):
    if birth:
        return str(birth)
    return ""

@app.callback(
    Output('selected-motor', 'children'),
    [Input('auto-motor-input', 'value')]
)
def update_mator(motor):
    if motor:
        return str(motor)
    return ""

@app.callback(
    Output('selected-fuel', 'children'),
    [Input('auto-fuel-dropdown', 'value')]
)
def update_fuel(fuel):
    if fuel:
        return str(fuel)
    return ""

@app.callback(
    Output('selected-egalik', 'children'),
    [Input('auto-owner-button', 'value')]
)
def update_egalik(egalik):
    if egalik:
        return str(egalik)
    return ""

@app.callback(
    Output('selected-kuzov', 'children'),
    [Input('auto-kuzov-dropdown', 'value')]
)
def update_kuzov(kuzov):
    if kuzov:
        return str(kuzov)
    return ""

@app.callback(
    Output('selected-color', 'children'),
    [Input('auto-color-dropdown', 'value')]
)
def update_color(color):
    if color:
        return str(color)
    return ""

@app.callback(
    Output('selected-condition', 'children'),
    [Input('auto-condition-dropdown', 'value')]
)
def update_condition(condition):
   
    if condition:
        return str(condition)
    return ""

@app.callback(
    Output('selected-features', 'children'),
    [Input('auto-feature-dropdown', 'value')]
)
def update_features(features):
    if features:
        return ", ".join(features)
    return ""

@app.callback(
    Output('selected-ownerCount', 'children'),
    [Input('auto-ownerCount-input', 'value')]
)
def update_ownerCount(ownerCount):
    if ownerCount:
        return str(ownerCount)
    return ""

@app.callback(
    Output('selected-probeg', 'children'),
    [Input('auto-probeg-input', 'value')]
)
def update_probeg(probeg):
    
    if probeg:
        return str(probeg)
    return ""

@app.callback(
    Output('selected-transmission', 'children'),
    [Input('auto-transmission-button', 'value')]
)
def update_transmission(transmission):
   
    if transmission:
        return (transmission)
    return ""

@app.callback(
    Output('auto-selected-time', 'children'),
    [Input('auto-oy-input', 'value'),
     Input('auto-year-input', 'value')]
)
def update_time(month, year):
    if month and year:
        return f"{month}-{year}"
    return ""

#############################LInk auto pdf generator######################################################################
@app.callback(
    Output('download-button-auto', 'disabled'),
    [Input('auto-price', 'children')]
)
def toggle_download_button(price):
    if price and price != "Baholash tugmasini bosing" and not isinstance(price, dict):
        return False
    return True
@app.callback(
    Output("download-pdf-auto", "data"),
    Input("download-button-auto", "n_clicks"),
    [State('auto-selected-hudud', 'children'),
     State('selected-brend', 'children'),
     State('selected-name', 'children'),
     State('selected-birth', 'children'),
     State('selected-motor', 'children'),
     State('selected-fuel', 'children'),
     State('selected-egalik', 'children'),
     State('selected-kuzov', 'children'),
     State('selected-color', 'children'),
     State('selected-condition', 'children'),
     State('selected-features', 'children'),
     State('selected-ownerCount', 'children'),
     State('selected-probeg', 'children'),
     State('selected-transmission', 'children'),
     State('auto-selected-time', 'children'),
     State('auto-price', 'children'),
     State('auto-price-range', 'children')],
    prevent_initial_call=True
)
def generate_pdf(n_clicks, hudud, brend, name, birth, motor, fuel, egalik, kuzov, 
                color, condition, features, ownerCount, probeg, transmission, 
                time_value, price, price_range):
    if not n_clicks:
        return no_update
        
    # Create a dictionary of property details
    property_details = {
        'Hudud': hudud,
        'Brend': brend,
        'Nomi': name,
        'Ishlab chiqarilgan yili': birth,
        'Mator hajmi': motor,
        "Yoqilg'gi turi": fuel,
        'Egalik turi': egalik,
        'Kuzov turi': kuzov,
        'Rangi': color,
        'Holati': condition,
        "Qo'shimcha narsalari": features,
        'Oldingi egalari soni': ownerCount,
        'Yurgan masofasi': probeg,
        'Kuchlanishi': transmission,
        'Baholash vaqti': time_value
    }
    
    # Generate PDF
    try:
        pdf_bytes = create_report_auto(property_details, price.replace('$', '').replace(',', ''), price_range)

        # Record download event
        try:
            events = load_prediction_counts()
            new_event = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'home': 0,
                'auto': 0,
                'home_downloads': 0,
                'auto_downloads': 1
            }
            events.append(new_event)
            save_prediction_counts(events)
            print(f"\n[Link Auto] New download event recorded at {new_event['timestamp']}")
        except Exception as e:
            print(f"Error recording download event: {str(e)}")
        
        # Return the PDF as a download
        return dcc.send_bytes(pdf_bytes, f"linkauto_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return no_update





if __name__ == '__main__':
    app.run(debug=False)
    # app.run(debug=False,host='0.0.0.0',port='8050')
    
# Add at the end of the file, after all other callbacks
@app.callback(
    Output('home-prediction-count', 'children'),
    Input('submit-button', 'n_clicks'),
    State('house-price', 'children')
)
def update_home_prediction_count(n_clicks, price):
    if n_clicks is None or price is None:
        raise PreventUpdate
    
    if price != '':  # If there's a valid prediction
        add_prediction_event('home_predict')
        return ''  # Return empty string since we don't need to update UI
    
    raise PreventUpdate

@app.callback(
    Output('auto-prediction-count', 'children'),
    Input('auto-submit-button', 'n_clicks'),
    State('auto-price', 'children')
)
def update_auto_prediction_count(n_clicks, price):
    if n_clicks is None or price is None:
        raise PreventUpdate
    
    if price != '':  # If there's a valid prediction
        add_prediction_event('auto_predict')
        return ''  # Return empty string since we don't need to update UI
    
    raise PreventUpdate

@app.callback(
    [Output('home-prediction-count', 'children', allow_duplicate=True),
     Output('auto-prediction-count', 'children', allow_duplicate=True)],
    Input('_', 'children')
)
def initialize_prediction_counts(_):
    return prediction_events['home'], prediction_events['auto']