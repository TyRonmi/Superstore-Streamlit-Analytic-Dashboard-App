import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')
import plotly.figure_factory as ff
import requests

# Set page config
st.set_page_config(
    page_title="Superstore",
    page_icon=":bar_chart:",
    layout="wide"
)

# Project description
st.title(" :bar_chart: Sample Superstore EDA")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
st.write("**This is an exploratory data analysis of a Superstore dataset.**")
st.write("Data source: [Here](https://data.world/missdataviz/superstore-2021)")
st.write("Download Data Here: [Here](https://data.world/missdataviz/superstore-2021/workspace/file?filename=Sample+-+Superstore.xls)")
st.write("---")

@st.cache_data
def load_data(file):
    if file.type in ["text/csv", "text/plain"]:
        df = pd.read_csv(file, encoding="ISO-8859-1")
    elif file.type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
        df = pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format")
    return df

st.write('*Data taking too long to load from data.world? Upload the Superstore data file*')

# File upload
fl = st.file_uploader(":file_folder: Upload file", type=["csv", "txt", "xlsx", "xls"])
if fl is not None:
    with st.spinner("Loading data..."):
        df = load_data(fl)
    st.success("Data loaded successfully.")
else:
    file_path = 'https://query.data.world/s/73qjpswpfbmeljx2k5ki6bbutw7qv6?dws=00000'
    try:
        df = pd.read_excel(file_path)  # Or Load data directly from the URL
        st.success("Data loaded successfully.")
    except ValueError as e:
        st.error(str(e))

col1, col2 = st.columns((2))
df["order_date"] = pd.to_datetime(df["Order Date"])

# Getting the min and max date
startDate = pd.to_datetime(df["order_date"]).min()
endDate = pd.to_datetime(df["order_date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["order_date"] >= date1) & (df["order_date"] <= date2)].copy()


st.sidebar.header("Select Options")
st.sidebar.write("##")

# select Region sidebar
region = st.sidebar.multiselect("**Select Region :**", df["Region"].unique())
if not region:
    regionDf = df.copy()
else:
    regionDf = df[df["Region"].isin(region)]

# select State sidebar
state = st.sidebar.multiselect("**Select State :**", regionDf["State"].unique())
if not state:
    stateDf = regionDf.copy()
else:
    stateDf = regionDf[regionDf["State"].isin(state)]

# select city sidebar
city = st.sidebar.multiselect("**Select City :**", stateDf["City"].unique())

# filtering data based on region, state and city
if not region and not state and not city:
    filteredDF = df
elif not state and not city:
    filteredDF = df[df["Region"].isin(region)]
elif not region and not city:
    filteredDF = regionDf[regionDf["State"].isin(state)]
elif region and state:
    filteredDF = df[df["Region"].isin(region) & regionDf["State"].isin(state)]
elif city:
    filteredDF = stateDf[stateDf["City"].isin(city)]
elif region and city:
    filteredDF = df[df["Region"].isin(region) & stateDf["City"].isin(city)]
elif state and city:
    filteredDF = regionDf[regionDf["State"].isin(state) & stateDf["City"].isin(city)]
else:
    filteredDF = df[df["Region"].isin(region) & regionDf["State"].isin(state) & stateDf["City"].isin(city)]

col1, col2 = st.columns(2)

# category, sub_category x sales
cateOrSubCate = st.radio(
    "Sales by Category and Sub-Category",
    ["Sales by Category", "Sales by Sub-Category"])
categoryDF = filteredDF.groupby(by = ["Category"], as_index = False)["Sales"].sum()
sub_categoryDF = filteredDF.groupby(by = ["Sub-Category"], as_index = False)["Sales"].sum()
if cateOrSubCate == 'Sales by Category':
    with col1:
        st.subheader("Sales by Category")
        cateSaleFig = px.bar(categoryDF, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in categoryDF["Sales"]], 
                         template="seaborn")
        st.plotly_chart(cateSaleFig, use_container_width=True, height = 200)

        with st.expander("View Sales by Category Data"):
            st.write(categoryDF.style.background_gradient(cmap="Blues"))
            csv = categoryDF.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="Sales_Category.csv", mime="text/csv",
                               help="click here to download Category Sales csv data")

else:
    sub_categoryDF = filteredDF.groupby(by = ["sub_category"], as_index = False)["sales"].sum()
    with col1:
        st.subheader("Sales by Sub-Category")
        subCateSaleFig = px.bar(sub_categoryDF, x="Sub-Category", y="Sales", text=['${:,.2f}'.format(x) for x in sub_categoryDF["Sales"]], 
                         template="seaborn")
        st.plotly_chart(subCateSaleFig, use_container_width=True, height = 200)

        with st.expander("View Sales by Sub-Category Data"):
            st.write(sub_categoryDF.style.background_gradient(cmap="Blues"))
            csv = categoryDF.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="Sales_Sub_Category.csv", mime="text/csv",
                               help="click here to download Sub_Category Sales csv data")


with col2:
    st.subheader("Sales by Region")
    regSaleFig = px.pie(filteredDF, values="Sales", names="Region", hole=0.5)
    regSaleFig.update_traces(text=filteredDF["Region"], textposition="outside")
    st.plotly_chart(regSaleFig, use_container_width=True)

    with st.expander("View Sales by Region Data"):
        regionData = filteredDF.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(regionData.style.background_gradient(cmap="Oranges"))
        csv = regionData.to_csv(index=False).encode('utf-8')
        st.download_button("Dowload Region Data", data=csv, file_name="Region_Sales.csv", mime="text/csv",
                           help="Click here to download Regional Sales csv data")

st.write("---")

timeSalesProfit = st.radio(
    "Time Series Analysis of Sales and Profit",
    ["Time Series Analysis of Sales", "Time Series Analysis of Profit"])
#create a month-year column for time series analysis
filteredDF["month_year"] = filteredDF["order_date"].dt.to_period("M")

if timeSalesProfit == 'Time Series Analysis of Sales':
    st.subheader("Time Series Analysis of Sales")
    linechartSales = pd.DataFrame(filteredDF.groupby(filteredDF["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
    fig2 = px.line(linechartSales, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, width=1000, template="gridon")
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("View Time Series Data of Sales"):
        st.write(linechartSales.T.style.background_gradient(cmap="Blues"))
        csv = linechartSales.to_csv(index=False).encode('utf-8')
        st.download_button("Dowload Time Series Data", data=csv, file_name="Time_Series.csv", mime="text/csv",
                           help="Click here to download Time Series csv data")

else:
    st.subheader("Time Series Analysis of Profit")
    linechartProfit = pd.DataFrame(filteredDF.groupby(filteredDF["month_year"].dt.strftime("%Y : %b"))["profit"].sum()).reset_index()
    fig2 = px.line(linechartProfit, x="month_year", y="profit", labels={"profit": "Amount"}, height=500, width=1000, template="gridon")
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("View Time Series Data of Profit"):
        st.write(linechartProfit.T.style.background_gradient(cmap="Blues"))
        csv = linechartProfit.to_csv(index=False).encode('utf-8')
        st.download_button("Dowload Time Series Data", data=csv, file_name="Time_Series.csv", mime="text/csv",
                           help="Click here to download Time Series csv data")

#create treemap based on Region, category, sub-category
st.write("##")
st.write("---")
st.subheader("Hierarchical View of Sales Using Treemap")
fig3 = px.treemap(filteredDF, path=["Region","Category","Sub-Category"], values="Sales", hover_data=["Sales"],
                  color="Sub-Category")

# Calculate percentages for each item in the treemap
total_sales = filteredDF['Sales'].sum()
filteredDF['percentage'] = (filteredDF['Sales'] / total_sales) * 100
fig3.update_traces(textinfo='label+percent entry')

fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)
st.write("---")

#profits by category and sub_category
pie1, pie2 = st.columns(2)

with pie1:
    st.subheader("Profits by Sub_category")
    fig4 = px.pie(filteredDF, values="Profit", names="Sub-Category", template="plotly_dark")
    fig4.update_traces(text=filteredDF["Sub-Category"], textposition="inside")
    st.plotly_chart(fig4, use_container_width=True)

with pie2:
    st.subheader("Profits by Category")
    fig5 = px.pie(filteredDF, values="Profit", names="Category", template="plotly_dark")
    fig5.update_traces(text=filteredDF["Category"], textposition="inside")
    st.plotly_chart(fig5, use_container_width=True)
st.write("---")

# creating a table with specific columns only
st.subheader(":point_down: Table Summary")
with st.expander("Click here to view table"):
    n = st.slider("**select number of rows**", 5, 100, 10)
    sampleDf = filteredDF[0:n][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig6 = ff.create_table(sampleDf, colorscale="Cividis")
    st.plotly_chart(fig6, use_container_width=True)

    st.write("**Monthly Sub_Category Sales Table**")
    filteredDF["month"] = filteredDF["Order Date"].dt.month_name()
    sub_category_year = pd.pivot_table(data=filteredDF, values="Sales", index=["Sub-Category"], columns="month")
    st.write(sub_category_year.style.background_gradient(cmap="Blues"))
st.write("---")

# visualizing relationship between sales and profit using scatter plot
saleProfRel = px.scatter(filteredDF, x='Sales', y='Profit', size='Quantity')
saleProfRel['layout'].update(title='Sales & Profits Relationship', titlefont=dict(size=20),
                             xaxis=dict(title='Sales', titlefont=dict(size=20)),
                             yaxis=dict(title='Profit', titlefont=dict(size=20)))
st.plotly_chart(saleProfRel, use_container_width=True)

# download datasets
st.write("##")
st.write("---")
st.subheader(":inbox_tray: Download Section")
col1, col2, col3 = st.columns(3)
with col1:
    st.write("**Download Data Based on Selections**")
    csv = filteredDF.to_csv(index=False).encode('utf-8')
    st.download_button('Download Selected Data', data=csv, file_name='Selected_data.csv', mime="text/csv")

with col3:
    st.write("**Download Original Dataset**")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button('Download Main Data', data=csv, file_name='Original_data.csv', mime="text/csv")
