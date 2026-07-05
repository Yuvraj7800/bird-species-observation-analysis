import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="🐦 Bird Species Observation Analysis",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

UNIT_NAMES = {
    'ANTI': 'Antietam National Battlefield',
    'CATO': 'Catoctin Mountain Park',
    'CHOH': 'Chesapeake & Ohio Canal NHP',
    'GWMP': 'George Washington Memorial Pkwy',
    'HAFE': 'Harpers Ferry NHP',
    'MANA': 'Manassas National Battlefield',
    'MONO': 'Monocacy National Battlefield',
    'NACE': 'National Capital East Parks',
    'PRWI': 'Prince William Forest Park',
    'ROCR': 'Rock Creek Park',
    'WOTR': 'Wolf Trap National Park'
}

ADMIN_UNITS = list(UNIT_NAMES.keys())
HAB_COLORS  = {'Forest': '#2E8B57', 'Grassland': '#DAA520'}

# ─────────────────────────────────────────────
# DATA LOADING (cached)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data…")
def load_data():
    def read_sheets(path):
        frames = []
        for sheet in ADMIN_UNITS:
            try:
                df = pd.read_excel(path, sheet_name=sheet)
                df['Sheet_Source'] = sheet
                frames.append(df)
            except Exception:
                pass
        return pd.concat(frames, ignore_index=True)

    df_f = read_sheets("Bird_Monitoring_Data_FOREST.XLSX")
    df_g = read_sheets("Bird_Monitoring_Data_GRASSLAND.XLSX")
    df_g.rename(columns={'TaxonCode': 'NPSTaxonCode'}, inplace=True)

    for col in df_f.columns:
        if col not in df_g.columns:
            df_g[col] = np.nan
    for col in df_g.columns:
        if col not in df_f.columns:
            df_f[col] = np.nan

    df = pd.concat([df_f, df_g], ignore_index=True)

    # Clean
    cat_cols = ['Sub_Unit_Code','Site_Name','Sex','Sky','Wind','Disturbance',
                'ID_Method','Distance','Common_Name','Scientific_Name','AOU_Code']
    for c in cat_cols:
        if c in df.columns:
            df[c].fillna('Unknown', inplace=True)
    for c in ['Temperature','Humidity','Initial_Three_Min_Cnt']:
        if c in df.columns:
            df[c].fillna(df[c].median(), inplace=True)
    for c in ['PIF_Watchlist_Status','Regional_Stewardship_Status','Flyover_Observed']:
        if c in df.columns:
            df[c].fillna(False, inplace=True)

    df['Date']      = pd.to_datetime(df['Date'], errors='coerce')
    df['Month']     = df['Date'].dt.month
    df['Month_Name']= df['Date'].dt.strftime('%b')
    df['Year']      = df['Year'].astype('Int64')
    df['DayOfWeek'] = df['Date'].dt.day_name()

    def season(m):
        if m in [12,1,2]:  return 'Winter'
        if m in [3,4,5]:   return 'Spring'
        if m in [6,7,8]:   return 'Summer'
        return 'Autumn'
    df['Season'] = df['Month'].apply(season)

    df['Temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
    df['Humidity']    = pd.to_numeric(df['Humidity'],    errors='coerce')
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

df_full = load_data()

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/A_small_cup_of_coffee.JPG/240px-A_small_cup_of_coffee.JPG",
                 use_column_width=True, caption="")  # placeholder visual
st.sidebar.title("🔎 Filters")

habitats = st.sidebar.multiselect(
    "Habitat Type", options=df_full['Location_Type'].dropna().unique().tolist(),
    default=df_full['Location_Type'].dropna().unique().tolist()
)

years = sorted(df_full['Year'].dropna().unique().tolist())
year_range = st.sidebar.select_slider(
    "Year Range", options=years, value=(min(years), max(years))
)

admin_units = st.sidebar.multiselect(
    "Administrative Unit", options=ADMIN_UNITS, default=ADMIN_UNITS
)

seasons = st.sidebar.multiselect(
    "Season", options=['Spring','Summer','Autumn','Winter'],
    default=['Spring','Summer','Autumn','Winter']
)

watchlist_filter = st.sidebar.radio(
    "PIF Watchlist Status", ["All", "At-Risk Only", "Safe Only"]
)

# Apply filters
df = df_full.copy()
df = df[df['Location_Type'].isin(habitats)]
df = df[df['Year'].between(year_range[0], year_range[1])]
df = df[df['Admin_Unit_Code'].isin(admin_units)]
df = df[df['Season'].isin(seasons)]
if watchlist_filter == "At-Risk Only":
    df = df[df['PIF_Watchlist_Status'] == True]
elif watchlist_filter == "Safe Only":
    df = df[df['PIF_Watchlist_Status'] == False]

st.sidebar.markdown("---")
st.sidebar.metric("Records after filter", f"{len(df):,}")
st.sidebar.metric("Unique Species", f"{df['Scientific_Name'].nunique():,}")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("🐦 Bird Species Observation Analysis")
st.markdown("**Domain:** Environmental Studies · Biodiversity Conservation · Ecology")
st.markdown("---")

# ─────────────────────────────────────────────
# TAB LAYOUT
# ─────────────────────────────────────────────
tabs = st.tabs([
    "📊 Overview",
    "📅 Temporal",
    "📍 Spatial",
    "🦅 Species",
    "🌡️ Environment",
    "📏 Behavior",
    "👁️ Observers",
    "🚨 Conservation",
    "🗄️ SQL Queries"
])

SEASON_ORDER = ['Spring','Summer','Autumn','Winter']
MONTH_ORDER  = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# ════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ════════════════════════════════════════════
with tabs[0]:
    st.subheader("📊 Dashboard Overview")

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Observations", f"{len(df):,}")
    c2.metric("Unique Species",      f"{df['Scientific_Name'].nunique():,}")
    c3.metric("Admin Units",         f"{df['Admin_Unit_Code'].nunique()}")
    c4.metric("At-Risk Species",     f"{df[df['PIF_Watchlist_Status']==True]['Scientific_Name'].nunique()}")
    c5.metric("Observers",           f"{df['Observer'].nunique()}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        hab = df['Location_Type'].value_counts().reset_index()
        hab.columns = ['Habitat','Count']
        fig = px.pie(hab, names='Habitat', values='Count', hole=0.4,
                     color='Habitat', color_discrete_map=HAB_COLORS,
                     title="Observations by Habitat")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        rich = df.groupby('Admin_Unit_Code')['Scientific_Name'].nunique().sort_values(ascending=False).reset_index()
        rich.columns = ['Unit','Unique_Species']
        fig = px.bar(rich, x='Unit', y='Unique_Species', color='Unique_Species',
                     color_continuous_scale='Greens', title="Species Richness by Admin Unit")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        seas = df['Season'].value_counts().reindex(SEASON_ORDER).reset_index()
        seas.columns = ['Season','Count']
        fig = px.bar(seas, x='Season', y='Count', color='Season',
                     title="Observations by Season",
                     color_discrete_sequence=['#FF7F0E','#FFD700','#8B4513','#1f77b4'])
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        wl = df['PIF_Watchlist_Status'].map({True:'At Risk',False:'Safe'}).value_counts().reset_index()
        wl.columns = ['Status','Count']
        fig = px.pie(wl, names='Status', values='Count', hole=0.4,
                     color='Status', color_discrete_map={'At Risk':'#DC143C','Safe':'#90EE90'},
                     title="PIF Watchlist Status")
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════
# TAB 2 — TEMPORAL
# ════════════════════════════════════════════
with tabs[1]:
    st.subheader("📅 Temporal Analysis")

    yearly = df.groupby(['Year','Location_Type']).size().reset_index(name='Observations')
    fig = px.line(yearly, x='Year', y='Observations', color='Location_Type',
                  markers=True, color_discrete_map=HAB_COLORS,
                  title="Yearly Observations by Habitat")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        monthly = df.groupby(['Month_Name','Location_Type']).size().reset_index(name='Obs')
        monthly['Month_Name'] = pd.Categorical(monthly['Month_Name'], categories=MONTH_ORDER, ordered=True)
        monthly.sort_values('Month_Name', inplace=True)
        fig = px.bar(monthly, x='Month_Name', y='Obs', color='Location_Type',
                     barmode='group', color_discrete_map=HAB_COLORS,
                     title="Monthly Observations")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        seasonal = df.groupby(['Season','Location_Type']).size().reset_index(name='Obs')
        seasonal['Season'] = pd.Categorical(seasonal['Season'], categories=SEASON_ORDER, ordered=True)
        seasonal.sort_values('Season', inplace=True)
        fig = px.bar(seasonal, x='Season', y='Obs', color='Location_Type',
                     barmode='group', color_discrete_map=HAB_COLORS,
                     title="Seasonal Observations")
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap
    hm = df.groupby(['Year','Month']).size().unstack(fill_value=0)
    hm.columns = [MONTH_ORDER[m-1] for m in hm.columns]
    fig = px.imshow(hm, text_auto=True, color_continuous_scale='YlGn',
                    title="Year × Month Observation Heatmap", aspect='auto')
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════
# TAB 3 — SPATIAL
# ════════════════════════════════════════════
with tabs[2]:
    st.subheader("📍 Spatial Analysis")

    col1, col2 = st.columns(2)
    with col1:
        admin_obs = df.groupby('Admin_Unit_Code').size().sort_values(ascending=False).reset_index(name='Observations')
        fig = px.bar(admin_obs, x='Admin_Unit_Code', y='Observations',
                     text='Observations', color='Observations',
                     color_continuous_scale='Blues',
                     title="Total Observations per Admin Unit")
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        admin_div = df.groupby('Admin_Unit_Code')['Scientific_Name'].nunique().sort_values(ascending=False).reset_index(name='Unique_Species')
        fig = px.bar(admin_div, x='Admin_Unit_Code', y='Unique_Species',
                     text='Unique_Species', color='Unique_Species',
                     color_continuous_scale='Tealgrn',
                     title="Species Diversity per Admin Unit")
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    # Species richness by habitat per unit
    rich2 = df.groupby(['Admin_Unit_Code','Location_Type'])['Scientific_Name'].nunique().reset_index()
    rich2.columns = ['Unit','Habitat','Species']
    fig = px.bar(rich2, x='Unit', y='Species', color='Habitat',
                 barmode='group', color_discrete_map=HAB_COLORS,
                 title="Species Richness: Forest vs Grassland per Admin Unit")
    st.plotly_chart(fig, use_container_width=True)

    top_plots = df['Plot_Name'].value_counts().head(15).reset_index()
    top_plots.columns = ['Plot','Observations']
    fig = px.bar(top_plots, y='Plot', x='Observations', orientation='h',
                 text='Observations', color='Observations',
                 color_continuous_scale='Oranges',
                 title="Top 15 Most Active Observation Plots")
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════
# TAB 4 — SPECIES
# ════════════════════════════════════════════
with tabs[3]:
    st.subheader("🦅 Species Analysis")

    n_species = st.slider("Number of top species to show", 5, 30, 20)
    top_sp = df['Common_Name'].value_counts().head(n_species).reset_index()
    top_sp.columns = ['Common_Name','Count']
    fig = px.bar(top_sp, y='Common_Name', x='Count', orientation='h',
                 text='Count', color='Count',
                 color_continuous_scale='Viridis',
                 title=f"Top {n_species} Most Observed Species")
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        forest_sp    = set(df[df['Location_Type']=='Forest']['Scientific_Name'])
        grassland_sp = set(df[df['Location_Type']=='Grassland']['Scientific_Name'])
        labels = ['Forest Only','Grassland Only','Shared']
        values = [len(forest_sp-grassland_sp), len(grassland_sp-forest_sp), len(forest_sp&grassland_sp)]
        fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.4,
                               marker_colors=['#2E8B57','#DAA520','#4682B4']))
        fig.update_layout(title='Species Habitat Exclusivity')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        id_m = df['ID_Method'].value_counts().reset_index()
        id_m.columns = ['Method','Count']
        fig = px.pie(id_m, names='Method', values='Count', hole=0.3,
                     title="Identification Method Distribution")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        sex_df = df[df['Sex'].isin(['Male','Female','Undetermined'])]
        sex_hab = sex_df.groupby(['Location_Type','Sex']).size().reset_index(name='Count')
        fig = px.bar(sex_hab, x='Location_Type', y='Count', color='Sex',
                     barmode='group', title="Sex Ratio by Habitat",
                     color_discrete_map={'Male':'#1f77b4','Female':'#e377c2','Undetermined':'#7f7f7f'})
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        intvl = df['Interval_Length'].value_counts().reset_index()
        intvl.columns = ['Interval','Count']
        fig = px.bar(intvl, x='Interval', y='Count', text='Count',
                     color='Count', color_continuous_scale='Oranges',
                     title="Observation Interval Lengths")
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    # Sunburst
    sb = df.groupby(['Location_Type','Admin_Unit_Code','Common_Name']).size().reset_index(name='Count')
    sb = sb.sort_values('Count',ascending=False).groupby(['Location_Type','Admin_Unit_Code']).head(3)
    fig = px.sunburst(sb, path=['Location_Type','Admin_Unit_Code','Common_Name'],
                      values='Count', color='Location_Type', color_discrete_map=HAB_COLORS,
                      title="Sunburst: Habitat → Admin Unit → Top Species")
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════
# TAB 5 — ENVIRONMENT
# ════════════════════════════════════════════
with tabs[4]:
    st.subheader("🌡️ Environmental Conditions")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(df, x='Temperature', color='Location_Type',
                           barmode='overlay', nbins=40, opacity=0.7, marginal='box',
                           color_discrete_map=HAB_COLORS,
                           title="Temperature Distribution by Habitat")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(df, x='Humidity', color='Location_Type',
                           barmode='overlay', nbins=40, opacity=0.7, marginal='box',
                           color_discrete_map=HAB_COLORS,
                           title="Humidity Distribution by Habitat")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig = px.box(df, x='Season', y='Temperature', color='Location_Type',
                     category_orders={'Season':SEASON_ORDER},
                     color_discrete_map=HAB_COLORS,
                     title="Temperature by Season & Habitat")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        sky = df.groupby(['Sky','Location_Type']).size().reset_index(name='Count')
        sky.sort_values('Count', ascending=False, inplace=True)
        fig = px.bar(sky, x='Sky', y='Count', color='Location_Type',
                     barmode='group', color_discrete_map=HAB_COLORS,
                     title="Observations by Sky Condition")
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        wind = df['Wind'].value_counts().head(8).reset_index()
        wind.columns = ['Wind','Count']
        fig = px.bar(wind, y='Wind', x='Count', orientation='h',
                     color='Count', color_continuous_scale='Blues',
                     title="Top Wind Conditions")
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        disturb = df['Disturbance'].value_counts().reset_index()
        disturb.columns = ['Disturbance','Count']
        fig = px.pie(disturb, names='Disturbance', values='Count',
                     title="Disturbance Levels")
        st.plotly_chart(fig, use_container_width=True)

    # Correlation heatmap
    num_df = df[['Temperature','Humidity','Initial_Three_Min_Cnt','Visit','Month']].dropna()
    corr = num_df.corr().round(2)
    fig = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r',
                    title="Correlation Matrix of Numerical Features")
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════
# TAB 6 — BEHAVIOR
# ════════════════════════════════════════════
with tabs[5]:
    st.subheader("📏 Distance & Behavior Analysis")

    col1, col2 = st.columns(2)
    with col1:
        dist = df.groupby(['Distance','Location_Type']).size().reset_index(name='Count')
        fig = px.bar(dist, x='Distance', y='Count', color='Location_Type',
                     barmode='group', color_discrete_map=HAB_COLORS,
                     title="Observation Distance by Habitat")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fly = df.groupby(['Flyover_Observed','Location_Type']).size().reset_index(name='Count')
        fly['Type'] = fly['Flyover_Observed'].map({True:'Flyover',False:'Non-Flyover'})
        fig = px.bar(fly, x='Location_Type', y='Count', color='Type',
                     barmode='group',
                     title="Flyover vs Non-Flyover Observations")
        st.plotly_chart(fig, use_container_width=True)

    top_cnt = df.groupby('Common_Name')['Initial_Three_Min_Cnt'].sum().sort_values(ascending=False).head(15).reset_index()
    top_cnt.columns = ['Species','Count']
    fig = px.bar(top_cnt, y='Species', x='Count', orientation='h',
                 text='Count', color='Count', color_continuous_scale='Plasma',
                 title="Top 15 Species by Total Initial 3-Min Count")
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════
# TAB 7 — OBSERVERS
# ════════════════════════════════════════════
with tabs[6]:
    st.subheader("👁️ Observer Trends")

    col1, col2 = st.columns(2)
    with col1:
        obs_rec = df['Observer'].value_counts().head(15).reset_index()
        obs_rec.columns = ['Observer','Records']
        fig = px.bar(obs_rec, y='Observer', x='Records', orientation='h',
                     text='Records', color='Records', color_continuous_scale='Purples',
                     title="Top 15 Observers by Records")
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        obs_div = df.groupby('Observer')['Scientific_Name'].nunique().sort_values(ascending=False).head(15).reset_index()
        obs_div.columns = ['Observer','Species']
        fig = px.bar(obs_div, y='Observer', x='Species', orientation='h',
                     text='Species', color='Species', color_continuous_scale='Teal',
                     title="Top 15 Observers by Species Diversity")
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    visits = df['Visit'].value_counts().sort_index().reset_index()
    visits.columns = ['Visit','Count']
    fig = px.bar(visits, x='Visit', y='Count', text='Count',
                 color='Count', color_continuous_scale='Sunset',
                 title="Visit Number Distribution")
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════
# TAB 8 — CONSERVATION
# ════════════════════════════════════════════
with tabs[7]:
    st.subheader("🚨 Conservation Insights")

    wl_df = df[df['PIF_Watchlist_Status']==True]
    col1, col2 = st.columns(2)
    c1, c2, c3 = st.columns(3)
    c1.metric("At-Risk Observations", f"{len(wl_df):,}")
    c2.metric("At-Risk Species",      f"{wl_df['Scientific_Name'].nunique()}")
    c3.metric("% of Total",           f"{100*len(wl_df)/max(len(df),1):.1f}%")

    wl_sp = wl_df['Common_Name'].value_counts().head(15).reset_index()
    wl_sp.columns = ['Species','Count']
    fig = px.bar(wl_sp, y='Species', x='Count', orientation='h',
                 text='Count', color='Count', color_continuous_scale='Reds',
                 title="Top 15 PIF Watchlist Species")
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        stew = df[df['Regional_Stewardship_Status']==True]
        stew_a = stew.groupby('Admin_Unit_Code')['Scientific_Name'].nunique().sort_values(ascending=False).reset_index()
        stew_a.columns = ['Unit','Priority_Species']
        fig = px.bar(stew_a, x='Unit', y='Priority_Species',
                     text='Priority_Species', color='Priority_Species',
                     color_continuous_scale='OrRd',
                     title="Regional Priority Species per Admin Unit")
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        wh = df.groupby(['Location_Type','PIF_Watchlist_Status']).size().reset_index(name='Count')
        wh['Status'] = wh['PIF_Watchlist_Status'].map({True:'At Risk',False:'Safe'})
        fig = px.bar(wh, x='Location_Type', y='Count', color='Status',
                     barmode='stack',
                     color_discrete_map={'At Risk':'#DC143C','Safe':'#90EE90'},
                     title="At-Risk vs Safe by Habitat")
        st.plotly_chart(fig, use_container_width=True)

    aou = df['AOU_Code'].value_counts().head(20).reset_index()
    aou.columns = ['AOU_Code','Count']
    fig = px.bar(aou, x='AOU_Code', y='Count', text='Count',
                 color='Count', color_continuous_scale='Cividis',
                 title="Top 20 AOU Codes")
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════
# TAB 9 — SQL QUERIES
# ════════════════════════════════════════════
with tabs[8]:
    st.subheader("🗄️ SQL-Based Analysis")
    st.markdown("Run live SQL queries against the filtered dataset:")

    # Build in-memory DB from filtered df
    @st.cache_data
    def build_db(data_hash):
        return None  # triggers reload

    conn = sqlite3.connect(':memory:')
    df_sql = df.copy()
    df_sql['Date'] = df_sql['Date'].astype(str)
    for c in ['PIF_Watchlist_Status','Regional_Stewardship_Status','Flyover_Observed']:
        df_sql[c] = df_sql[c].astype(int)
    df_sql.to_sql('bird_observations', conn, index=False, if_exists='replace')

    preset_queries = {
        "Habitat Summary": """
SELECT Location_Type AS Habitat,
       COUNT(*) AS Total_Obs,
       COUNT(DISTINCT Scientific_Name) AS Unique_Species
FROM bird_observations GROUP BY Location_Type ORDER BY Total_Obs DESC""",

        "Top 10 Species": """
SELECT Common_Name, Scientific_Name, COUNT(*) AS Observations
FROM bird_observations
GROUP BY Common_Name, Scientific_Name
ORDER BY Observations DESC LIMIT 10""",

        "Watchlist by Admin Unit": """
SELECT Admin_Unit_Code,
       COUNT(DISTINCT Scientific_Name) AS Watchlist_Species,
       COUNT(*) AS Total_Obs
FROM bird_observations WHERE PIF_Watchlist_Status=1
GROUP BY Admin_Unit_Code ORDER BY Watchlist_Species DESC""",

        "Seasonal Weather Averages": """
SELECT Season, Location_Type,
       ROUND(AVG(Temperature),2) AS Avg_Temp,
       ROUND(AVG(Humidity),2) AS Avg_Humidity,
       COUNT(*) AS Records
FROM bird_observations GROUP BY Season, Location_Type ORDER BY Season""",

        "Year-over-Year Trend": """
SELECT Year, Location_Type,
       COUNT(*) AS Observations,
       COUNT(DISTINCT Scientific_Name) AS Unique_Species
FROM bird_observations WHERE Year IS NOT NULL
GROUP BY Year, Location_Type ORDER BY Year""",

        "Top 10 Observers": """
SELECT Observer, COUNT(*) AS Records,
       COUNT(DISTINCT Scientific_Name) AS Unique_Species,
       COUNT(DISTINCT Admin_Unit_Code) AS Units_Covered
FROM bird_observations
GROUP BY Observer ORDER BY Unique_Species DESC LIMIT 10""",

        "Flyover Rate": """
SELECT Location_Type,
       SUM(Flyover_Observed) AS Flyover_Count,
       COUNT(*) AS Total,
       ROUND(100.0*SUM(Flyover_Observed)/COUNT(*),2) AS Flyover_Pct
FROM bird_observations GROUP BY Location_Type""",
    }

    col1, col2 = st.columns([1,3])
    with col1:
        selected_q = st.selectbox("Preset Queries", list(preset_queries.keys()))
    
    query_text = st.text_area("SQL Query (editable)", value=preset_queries[selected_q], height=150)

    if st.button("▶ Run Query"):
        try:
            result = pd.read_sql(query_text, conn)
            st.success(f"✅ {len(result)} rows returned")
            st.dataframe(result, use_container_width=True)
        except Exception as e:
            st.error(f"❌ SQL Error: {e}")

    conn.close()

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("**🐦 Bird Species Observation Analysis** · Environmental Studies & Biodiversity Conservation")
