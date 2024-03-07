import streamlit as st
import pandas as pd
import pydeck as pdk

#df = pd.read_excel("tokyo_charge_p2.xlsx")


uploaded_file = st.file_uploader("Excelファイルをアップロードしてください", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("アップロードされたデータ:")
    st.dataframe(df)

    # カテゴリーごとに色を割り当てる
    category_colors = {
        "その他": [105, 105, 105],
        "大規模小売店舗": [127, 255, 0],    # 淡い緑
        "宿泊施設": [0, 0, 255],        # 淡い青
        "自治体施設": [255, 255, 0],       # 淡い黄色
        "自動車ディーラー": [0, 0, 139],  # 
        "ガソリンスタンド": [255, 20, 147],  # 淡いピンク
        "ＳＡ/ＰＡ": [128, 0, 128],       
        "小売店舗": [255, 165, 0],       # 淡いオレンジ
        "ゴルフ場": [0, 128, 0],       # 明るい緑
        "コンビニエンスストア": [30, 144, 255],  # 明るい青
        "観光施設": [173, 255, 47]  # 明るい青
    }
    # サイドバー設定
    # 施設カテゴリの選択
    categories = df['施設カテゴリー'].unique()
    selected_categories = st.sidebar.multiselect('設置先施設名カテゴリを選択', categories, default=categories)

    # 「各充電器出力(kw)」でNaNでないもののみ表示するチェックボックス
    #kw_check = st.sidebar.checkbox('調査ずみ(稼働率は調査できてないっぽい')

    # データフィルタリング
    filtered_df = df[df['施設カテゴリー'].isin(selected_categories)]

    #if kw_check:
    #    filtered_df = filtered_df[filtered_df['各充電器出力(kw)'].notna()]

    # 施設カテゴリーごとの数と色を表示
    st.write("### 施設カテゴリーごとの数")
    for category in categories:
        count = df[df['施設カテゴリー'] == category].shape[0]
        color = f"rgb({category_colors[category][0]}, {category_colors[category][1]}, {category_colors[category][2]})"
        st.sidebar.markdown(f"<span style='color:{color}'>●</span> {category}: {count}", unsafe_allow_html=True)

    # 「各充電器出力(kw)」がNaNでないデータの数を表示
    #kw_count = df[df['各充電器出力(kw)'].notna()].shape[0]
    #st.write(f"###): {kw_count}")

    # 各カテゴリーに対応する色の列を追加
    filtered_df['color'] = filtered_df['施設カテゴリー'].apply(lambda x: category_colors.get(x, [200, 200, 200]))

    # 地図の表示
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=filtered_df['緯度'].mean(),
            longitude=filtered_df['経度'].mean(),
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=filtered_df,
                get_position='[経度, 緯度]',
                get_color='color',
                get_radius=200,
            ),
        ],
    ))

    st.dataframe(df)

    df_ev_charge = df[["設置場所名称","所在地","specified_heights"]]
    df_ev_map = df[["設置場所名称","緯度","経度","heights_sum"]]


    st.data_editor(
        df_ev_charge,
        column_config={
            "specified_heights": st.column_config.BarChartColumn(
                "ev_charge ",
                y_min=0,
                y_max=160,
            ),
        },
        hide_index=True,
    )
    time_list=["6時","7時","8時","9時","10時","11時","12時","13時","14時","15時","16時","17時","18時","19時","20時","21時","22時","23時","0時","1時","2時","3時","4時","5時"]
    selected_categories = []
    max_cols = 3
    num_categories = len(time_list)
    columns_per_row = min(num_categories, max_cols)

    # Streamlitの列オブジェクトを作成
    cols = st.sidebar.columns(columns_per_row)
    selected_categories = []

    # 各カテゴリーに対してチェックボックスを配置
    for i, category in enumerate(time_list):
        col_index = i % columns_per_row  # 現在の列のインデックスを計算
        # チェックボックスを配置し、デフォルトでチェックを入れる
        if cols[col_index].checkbox(f'{category}', key=category, value=True):
            selected_categories.append(category)

    df['sum'] = df[selected_categories].sum(axis=1)

    # 選択されたカテゴリに基づいてデータフィルタリング
    #filtered_df = df[df['Category'].isin(selected_categories)]


    # 地図の中心をデータの中心に設定
    midpoint = (df['緯度'].mean(), df['経度'].mean())

    # PyDeckで棒グラフを描画
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=midpoint[0],
            longitude=midpoint[1],
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'ColumnLayer',  # ColumnLayerを使用
                data=df,
                get_position='[経度, 緯度]',
                get_elevation='sum',  # 売上に応じて棒の高さを設定
                elevation_scale=1,  # 売上と棒の高さのスケールを調整
                radius=50,  # 棒の半径
                get_fill_color='[255, 165, 0, 255]',  # 棒の色（例: オレンジ）
                pickable=True,
                auto_highlight=True,
            ),
        ],
    ))

    st.write(df['緯度'].mean())
    st.write(df['経度'].mean())

    
