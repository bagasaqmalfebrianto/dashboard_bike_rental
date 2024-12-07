import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi halaman
st.set_page_config(page_title="Bike Rental Dashboard", layout='wide')

# CSS untuk mengubah warna background dan teks
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFFFFF;
    }
    h1, h2, h3, h4, h5, h6, p {
        color: #01314A !important;
    }
    [data-testid="stSidebar"] {
        background-color: #01314A;
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Membaca data dan memastikan kolom 'date' dalam format datetime

day_df = pd.read_csv('day_df.csv')
hour_df = pd.read_csv('hour_df.csv')
# day_df['date'] = pd.to_datetime(day_df['date'])  # Mengonversi kolom 'date' ke datetime
# hour_df['date'] = pd.to_datetime(hour_df['date'])  # Mengonversi kolom 'date' ke datetime


#KONFIGURASI DATETIME
datetime_col = ['date']
day_df.sort_values(by="date",inplace=True)
hour_df.sort_values(by="date",inplace=True)

for column in datetime_col:
    day_df[column] = pd.to_datetime(day_df[column])
    hour_df[column] = pd.to_datetime(hour_df[column])

min_date = day_df['date'].min()
max_date = day_df['date'].max()
min_date_hour = hour_df['date'].min()
max_date_hour = hour_df['date'].max()

# # Set kolom 'date' sebagai indeks
# day_df.set_index('date', inplace=True)
# hour_df.set_index('date', inplace=True)




# Judul halaman
st.title(":blue[Bike] Rental 🚴‍♂️")

num1, num2, num3, right_align = st.columns([1, 1, 1, 6])

with right_align:
    # Membuat container untuk memastikan elemen tetap di bagian atas
    with st.container():
        # Mengambil input tanggal dari pengguna
        start_date, end_date = st.date_input(
            label='Rentang Waktu', 
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )

day_main_df = day_df[(day_df["date"] >= str(start_date)) & 
                (day_df["date"] <= str(end_date))]

# Filter dataset hour_df berdasarkan rentang tanggal yang dipilih
hour_main_df = hour_df[(hour_df["date"] >= pd.to_datetime(str(start_date))) & 
                       (hour_df["date"] <= pd.to_datetime(str(end_date)))]



def total_sepeda_casual_registered_all(df):
    total = df.groupby(by=['year', 'month']).agg({
        'casual': ['sum', 'min', 'max', 'mean'],
        'registered': ['sum', 'min', 'max', 'mean'],
        'total_count':'sum'
    })
    return total

# Mengambil total sewa casual
total_sewa = total_sepeda_casual_registered_all(day_main_df)
total_sepeda_cas = total_sewa['casual']['sum'].sum()
total_sepeda_reg = total_sewa['registered']['sum'].sum()
total_sepeda_all = total_sewa['total_count']['sum'].sum()

with num1:
    st.metric("Total Sewa Casual:", value=total_sepeda_cas)

with num2:
    st.metric("Total Sewa Registered:", value=total_sepeda_reg)

with num3:
    st.metric("Total Sewa Menyeluruh:", value=total_sepeda_all)



# Fungsi untuk meresample data bulanan
def month_rental(data):
    # Meresample data berdasarkan bulan dengan mempertimbangkan kolom 'date'
    monthly_counts = data.resample(rule='M', on='date').agg({
        'total_count': 'sum'
    })
    # Menambahkan kolom tahun untuk pemisahan
    monthly_counts['year'] = monthly_counts.index.year
    # Mengubah index menjadi nama bulan
    monthly_counts.index = monthly_counts.index.strftime('%B')
    return monthly_counts

def count_season(data):
    # # Memfilter data untuk tahun 2011
    # data_2011 = data[data.index.year == 2011]
    
    # Mengelompokkan berdasarkan 'season' dan menghitung rata-rata 'total_count'
    grouped_cuaca = day_df.groupby('weathersit').agg({
    'total_count': 'mean'
    })

    
    return grouped_cuaca

# def count_weather(data):
#     # Mengelompokkan berdasarkan 'weathersit' dan menghitung rata-rata 'total_count'
#     grouped_musim = data.groupby('weathersit').agg({
#         'total_count': 'mean'
#     })
    
#     return grouped_musim

def get_top_hours_by_season(dataframe, filter_condition, top_n=1):
    # Filter data berdasarkan kondisi
    filtered_data = dataframe[filter_condition]

    # Mengelompokkan data berdasarkan 'season' dan 'hour', lalu menghitung rata-rata 'total_count'
    grouped_data = filtered_data.groupby(['season', 'hour']).agg({
        'total_count': 'mean'
    }).reset_index()

    # Mengambil n jam teratas untuk setiap musim berdasarkan 'total_count'
    top_hours = grouped_data.groupby('season').apply(lambda x: x.nlargest(top_n, 'total_count')).reset_index(drop=True)

    return top_hours

def count_registered(data):
    # data_2011 = data[data.index.year == 2011]
    total_count_df = data.groupby('season')[['registered', 'casual']].sum().reset_index()
    return total_count_df

def count_hour(data):
    # data_2011 = data[data.index.year == 2011]
    # Mengelompokkan data berdasarkan 'hour' dan 'season', lalu menghitung total jumlah sewa
    group_hour = data.groupby(['hour', 'season']).agg({'total_count': 'sum'}).reset_index()

    # Mengambil 3 jam teratas untuk setiap musim berdasarkan 'total_count'
    top3_hours = group_hour.groupby('season', as_index=False).apply(lambda x: x.nlargest(3, 'total_count')).reset_index(drop=True)
    return top3_hours

# Siapkan dataframe bulanan
monthly_rental_df = month_rental(day_main_df)
season_counts = count_season(day_main_df)
# weather_counts = count_weather(day_main_df)
registered_counts = count_registered(day_main_df)
hour_counts = count_hour(hour_main_df)
top5_per_season_workingday = get_top_hours_by_season(
    dataframe=hour_df,
    filter_condition=(hour_df['workingday'] == 1),
    top_n=1
)

# Hari libur atau libur nasional
top5_per_season_holiday = get_top_hours_by_season(
    dataframe=hour_df,
    filter_condition=((hour_df['workingday'] == 0) | (hour_df['holiday'] == 1)),
    top_n=1
)

col1, col2 = st.columns([3,2])
# Subheader
with col1:
    plt.figure(figsize=(10, 5))

    # Menggambarkan garis untuk tahun 2011
    plt.plot(
        monthly_rental_df[monthly_rental_df['year'] == 2011].index,
        monthly_rental_df[monthly_rental_df['year'] == 2011]['total_count'],
        marker='o', linewidth=2, color="#72BCD4", label='2011'
    )

    # Menggambarkan garis untuk tahun 2012
    plt.plot(
        monthly_rental_df[monthly_rental_df['year'] == 2012].index,
        monthly_rental_df[monthly_rental_df['year'] == 2012]['total_count'],
        marker='o', linewidth=2, color="#FF6347", label='2012'
    )

    # Menambahkan elemen visual lainnya
    plt.title("Penyewaan Rental dalam Periode Tahun 2011-2012", loc="center", fontsize=20)
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Total Count', fontsize=12)
    plt.grid()
    plt.legend()  # Menambahkan legenda untuk membedakan tahun

    # Tampilkan plot di Streamlit
    st.pyplot(plt)

with col2:
    # Mengatur warna yang berbeda kontras
    colors = ["#FF5733", "#3498DB", "#28B463", "#F39C12", "#9B59B6"]

    plt.figure(figsize=(10, 5))

    sns.barplot(
        data=season_counts,
        x='weathersit',
        y='total_count',
        palette=colors
    )

    plt.title("Rata-rata Penyewaan Berdasarkan Cuaca", fontsize=16)
    plt.xlabel("Cuaca", fontsize=12)
    plt.ylabel("Rata-rata Penyewaan", fontsize=12)
    plt.tick_params(axis='x', labelsize=10)
    plt.tick_params(axis='y', labelsize=10)
    st.pyplot(plt)

# with col3:
    # Mengatur warna yang berbeda kontras
    colors = ["#FF5733", "#3498DB", "#28B463", "#F39C12", "#9B59B6"]

    # Membuat figure dengan dua subplot sejajar (1 baris, 2 kolom)
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

    # Barplot untuk hari kerja
    sns.barplot(
        data=top5_per_season_workingday,
        x='season',
        y='hour',
        palette=colors,
        hue='season',
        ax=ax[0]
    )
    ax[0].set_ylabel(None)  # Tidak menampilkan label y
    ax[0].set_xlabel(None)  # Tidak menampilkan label x
    ax[0].set_title("Jam Tertinggi Penyewaan pada Hari Kerja", loc="center", fontsize=15)
    ax[0].tick_params(axis='y', labelsize=12)

    # Barplot untuk hari libur
    sns.barplot(
        data=top5_per_season_holiday,
        x='season',
        y='hour',
        palette=colors,
        hue='season',
        ax=ax[1]
    )
    ax[1].set_ylabel(None)  # Tidak menampilkan label y
    ax[1].set_xlabel(None)  # Tidak menampilkan label x
    ax[1].set_title("Jam Tertinggi Penyewaan pada Hari Libur", loc="center", fontsize=15)
    ax[1].tick_params(axis='y', labelsize=12)

    # Menambahkan judul utama untuk seluruh plot
    plt.suptitle("Jam Tertinggi Penyewaan pada Hari Kerja dan Hari Libur", fontsize=20)

    # Menampilkan plot
    st.pyplot(plt)

col4, col5 = st.columns([1,1])

with col4: 
    # Bar chart untuk jumlah yang terdaftar
    # st.subheader('Total Sepeda yang Disewakan Berdasarkan Musim')
    plt.figure(figsize=(10, 6))
    sns.barplot(x='registered', y='season', data=registered_counts, label='Registered', color='tab:blue')
    sns.barplot(x='casual', y='season', data=registered_counts, label='Casual', color='#FF6347')

    plt.title('Total Sepeda yang Disewakan pada 2 Tahun Terakhir Berdasarkan Musim', fontsize=16)
    plt.xlabel(None)
    plt.ylabel(None)
    plt.legend()
    st.pyplot(plt)

    # Mengatur warna yang berbeda kontras
    colors = ["#FF5733", "#3498DB", "#28B463", "#F39C12", "#9B59B6"]

    plt.figure(figsize=(15, 7.5))

with col5: 
    # Membuat grafik barplot

    # Mengatur warna yang berbeda kontras
    colors = ["#FF5733", "#3498DB", "#28B463", "#F39C12", "#9B59B6"]

    plt.figure(figsize=(15, 7.5))

    # Membuat grafik barplot
    sns.barplot(
        data=hour_counts,
        x='hour',
        y='total_count',
        palette=colors,
        hue='season'
    )

    # Menambahkan judul dan pengaturan label
    plt.title("3 Jam Teratas untuk Setiap Musim Berdasarkan Jumlah Sewa", fontsize=16)
    plt.xlabel("Jam", fontsize=12)
    plt.ylabel("Jumlah Sewa", fontsize=12)
    plt.tick_params(axis='x', labelsize=10)
    plt.tick_params(axis='y', labelsize=10)

    # Menampilkan legenda dan menampilkan grafik
    plt.legend(title='Musim', fontsize=10, title_fontsize=12)
    st.pyplot(plt)


