# import streamlit as st
# import pandas as pd
# import requests

# # Set page title
# st.set_page_config(page_title="Marginfi Liquidity Dashboard", layout="wide")

# # Function to fetch data from the API
# @st.cache_data(ttl=300)  # Cache the data for 5 minutes
# def fetch_data(url):
#     response = requests.get(url)
#     return response.json()

# # Main app
# def main():
#     st.title("Marginfi Liquidity Dashboard")

#     # Fetch data
#     url = "http://localhost:4137/marginfi/getBanksOverLiquidity"
#     data = fetch_data(url)

#     # Process data
#     df = pd.DataFrame(data)
#     df['Short Liquidity'] = df['tvl'].apply(lambda x: f"${x:,.2f}")
#     df['Long Liquidity'] = df['spotMarketData'].apply(lambda x: f"${x['formattedLiquidity']:,.2f}")
#     df['Market Cap'] = df['spotMarketData'].apply(lambda x: f"${x['formattedMC']:,.2f}")
#     df = df[['tokenSymbol', 'Short Liquidity', 'Long Liquidity', 'Market Cap']]
#     df = df.rename(columns={'tokenSymbol': 'Symbol'})

#     # Display table
#     st.dataframe(df, use_container_width=True)

#     # Add filters
#     st.sidebar.header("Filters")
#     min_short_liquidity = st.sidebar.number_input("Min Short Liquidity ($)", min_value=0, value=0, step=1000)
#     min_long_liquidity = st.sidebar.number_input("Min Long Liquidity ($)", min_value=0, value=0, step=1000)
#     min_market_cap = st.sidebar.number_input("Min Market Cap ($)", min_value=0, value=0, step=1000000)

#     # Apply filters
#     filtered_df = df[
#         (df['Short Liquidity'].apply(lambda x: float(x.replace('$', '').replace(',', ''))) >= min_short_liquidity) &
#         (df['Long Liquidity'].apply(lambda x: float(x.replace('$', '').replace(',', ''))) >= min_long_liquidity) &
#         (df['Market Cap'].apply(lambda x: float(x.replace('$', '').replace(',', ''))) >= min_market_cap)
#     ]

#     # Display filtered table
#     st.subheader("Filtered Data")
#     st.dataframe(filtered_df, use_container_width=True)

#     # Add some charts
#     st.subheader("Visualizations")
#     chart_data = df.copy()
#     chart_data['Short Liquidity'] = chart_data['Short Liquidity'].apply(lambda x: float(x.replace('$', '').replace(',', '')))
#     chart_data['Long Liquidity'] = chart_data['Long Liquidity'].apply(lambda x: float(x.replace('$', '').replace(',', '')))
#     chart_data['Market Cap'] = chart_data['Market Cap'].apply(lambda x: float(x.replace('$', '').replace(',', '')))

#     # Bar chart of top 10 tokens by Short Liquidity
#     st.bar_chart(chart_data.nlargest(10, 'Short Liquidity').set_index('Symbol')['Short Liquidity'])

#     # Scatter plot of Short vs Long Liquidity
#     st.scatter_chart(chart_data.set_index('Symbol')[['Short Liquidity', 'Long Liquidity']])

# if __name__ == "__main__":
#     main()
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

# Set page title
st.set_page_config(page_title="Marginfi Liquidity Dashboard", layout="wide")

# Function to fetch data from the API
@st.cache_data(ttl=300)  # Cache the data for 5 minutes
def fetch_data(url):
    response = requests.get(url)
    return response.json()

# Function to format large numbers
def format_large_number(num):
    if pd.isna(num):
        return "N/A"
    num = float(num)
    if num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    elif num >= 1e3:
        return f"${num/1e3:.2f}K"
    else:
        return f"${num:.2f}"

# Main app
def main():
    st.title("Marginfi Liquidity Dashboard")

    # Fetch data
    url = "http://159.223.14.10:4137/marginfi/getBanksOverLiquidity"
    data = fetch_data(url)

    # Process data
    df = pd.DataFrame(data)
    df['Short Liquidity'] = df['tvl'].apply(lambda x: float(x))
    df['Long Liquidity'] = df['spotMarketData'].apply(lambda x: float(x['formattedLiquidity']))
    df['FDV'] = df['spotMarketData'].apply(lambda x: float(x['formattedMC']))
    df['Short Liquidity Formatted'] = df['Short Liquidity'].apply(format_large_number)
    df['Long Liquidity Formatted'] = df['Long Liquidity'].apply(format_large_number)
    df['FDV Formatted'] = df['FDV'].apply(format_large_number)
    df['Liquidity Ratio'] = df['Long Liquidity'] / df['Short Liquidity']
    df = df[['tokenSymbol', 'Short Liquidity', 'Long Liquidity', 'FDV', 'Short Liquidity Formatted', 'Long Liquidity Formatted', 'FDV Formatted', 'Liquidity Ratio']]
    df = df.rename(columns={'tokenSymbol': 'Symbol'})

    # Display table with proper sorting
    st.dataframe(
        df[['Symbol', 'Short Liquidity', 'Long Liquidity', 'FDV', 'Liquidity Ratio']]
        .style
        .format({
            'Short Liquidity': format_large_number,
            'Long Liquidity': format_large_number,
            'FDV': format_large_number,
            'Liquidity Ratio': '{:.2f}'
        }),
        use_container_width=True
    )
    # Add filters
    st.sidebar.header("Filters")
    min_short_liquidity = st.sidebar.number_input("Min Short Liquidity ($)", min_value=0.0, value=0.0, step=1000.0)
    min_long_liquidity = st.sidebar.number_input("Min Long Liquidity ($)", min_value=0.0, value=0.0, step=1000.0)
    min_fdv = st.sidebar.number_input("Min FDV ($)", min_value=0.0, value=0.0, step=1000000.0)

    # Apply filters
    filtered_df = df[
        (df['Short Liquidity'] >= min_short_liquidity) &
        (df['Long Liquidity'] >= min_long_liquidity) &
        (df['FDV'] >= min_fdv)
    ]

    # Visualizations
    st.subheader("Visualizations")
    
    # 1. Long vs Short Liquidity Ratio
    st.subheader("1. Long vs Short Liquidity Ratio")
    st.markdown("""
    **Explanation:** The Liquidity Ratio is calculated as (Long Liquidity / Short Liquidity) for each asset. 
    - A ratio > 1 indicates more long liquidity than short liquidity.
    - A ratio < 1 indicates more short liquidity than long liquidity.
    - A ratio close to 1 suggests a balance between long and short liquidity.

    **Interpretation:**
    - High ratios might indicate strong bullish sentiment or potential overbought conditions.
    - Low ratios could suggest bearish sentiment or potential oversold conditions.
    - Assets with extreme ratios might present arbitrage opportunities or increased risk.
    """)
    fig_ratio = px.bar(filtered_df.sort_values('Liquidity Ratio', ascending=False), 
                       x='Symbol', y='Liquidity Ratio', 
                       title='Long vs Short Liquidity Ratio',
                       labels={'Liquidity Ratio': 'Long/Short Ratio'})
    st.plotly_chart(fig_ratio, use_container_width=True)

    # 2. Top 10 Assets by FDV
    fig_fdv = px.pie(filtered_df.nlargest(10, 'FDV'), values='FDV', names='Symbol', 
                     title='Top 10 Assets by FDV')
    st.plotly_chart(fig_fdv, use_container_width=True)

    # 3. Scatter plot of Short vs Long Liquidity
    st.subheader("3. Short vs Long Liquidity (Log Scale)")
    st.markdown("""
    **Explanation:** This scatter plot compares Short Liquidity to Long Liquidity for each asset on a logarithmic scale.
    - Each point represents an asset.
    - The x-axis shows Short Liquidity, and the y-axis shows Long Liquidity.
    - Both axes use a logarithmic scale to accommodate the wide range of values.

    **Interpretation:**
    - Assets closer to the diagonal line have a more balanced liquidity ratio.
    - Assets above the diagonal have more long liquidity relative to short liquidity.
    - Assets below the diagonal have more short liquidity relative to long liquidity.
    - The logarithmic scale helps visualize relationships for assets with widely different liquidity levels.
    """)
    fig_scatter = px.scatter(filtered_df, x='Short Liquidity', y='Long Liquidity', 
                             color='Symbol', hover_name='Symbol', 
                             log_x=True, log_y=True,
                             title='Short vs Long Liquidity (Log Scale)')
    st.plotly_chart(fig_scatter, use_container_width=True)

    # 4. Liquidity Distribution
    st.subheader("4. Distribution of Short and Long Liquidity")
    st.markdown("""
    **Explanation:** This box plot shows the distribution of Short and Long Liquidity across all assets.
    - The boxes represent the interquartile range (IQR) containing the middle 50% of the data.
    - The line inside the box is the median.
    - Whiskers extend to 1.5 times the IQR.
    - Points beyond the whiskers are potential outliers.

    **Interpretation:**
    - Compare the median and spread of Short vs Long Liquidity.
    - Identify potential outliers with exceptionally high or low liquidity.
    - Assess the overall liquidity landscape and how it differs between short and long positions.
    - The logarithmic scale on the y-axis helps visualize the wide range of liquidity values.
    """)
    fig_dist = go.Figure()
    fig_dist.add_trace(go.Box(y=filtered_df['Short Liquidity'], name='Short Liquidity'))
    fig_dist.add_trace(go.Box(y=filtered_df['Long Liquidity'], name='Long Liquidity'))
    fig_dist.update_layout(title='Distribution of Short and Long Liquidity', 
                           yaxis_type="log")
    st.plotly_chart(fig_dist, use_container_width=True)

    # 5. Correlation Heatmap
    st.subheader("5. Correlation Heatmap")
    st.markdown("""
    **Explanation:** This heatmap shows the correlation between different metrics:
    - Values range from -1 (strong negative correlation) to 1 (strong positive correlation).
    - 0 indicates no linear correlation.

    **Interpretation:**
    - Strong positive correlations appear in dark red.
    - Strong negative correlations appear in dark blue.
    - Look for unexpected correlations or lack of correlations.
    - Consider how these relationships might affect trading strategies or risk management.

    **Key relationships to observe:**
    - Short Liquidity vs Long Liquidity: Indicates overall market sentiment.
    - FDV vs Liquidity measures: Shows if higher-valued assets have more liquidity.
    - Liquidity Ratio vs other measures: Reveals how the balance of long/short liquidity relates to other factors.
    """)
    corr_df = filtered_df[['Short Liquidity', 'Long Liquidity', 'FDV', 'Liquidity Ratio']].corr()
    fig_heatmap = px.imshow(corr_df, text_auto=True, aspect="auto",
                            title='Correlation Heatmap')
    st.plotly_chart(fig_heatmap, use_container_width=True)

if __name__ == "__main__":
    main()