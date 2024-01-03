import pandas as pd
import requests
import json

api_df=pd.read_excel('PocketFm english.xlsx')
revenue_df=pd.read_excel('Show_Revenue($)_ENGLISH_Life_1703842054245.xlsx')

# Find show ids in B that do not exist in A
unique_show_ids = revenue_df[~revenue_df['show_id'].isin(api_df['show_id'])]

# Select 'show id' and 'title' columns for DataFrame C
res = unique_show_ids[['show_id', 'Show Title']]
def get_show_type(show_id):
    # Make an API call to retrieve show type based on show_id (Replace 'API_URL' with your API endpoint)
    headers = {
        'authority': 'api.cms.pocketfm.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'access-token': '2c114a38f03fe104242f750d264460ef2be8af35',
        'app-client': 'consumer-web',
        'app-version': '180',
        'auth-token': 'web-auth',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://cms.pocketfm.in',
        'pragma': 'no-cache',
        'referer': 'https://cms.pocketfm.in/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'uid': 'f2fbd9eb40de572b3d80a9aa81afe94706e82a2a',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    api_url = f"https://api.cms.pocketfm.com/v2/content_api/show.get_details?show_id={show_id}&info_level=min&curr_epoch=1690982603&is_novel=0"  # Replace 'your-api-url' with the actual API URL
    response = requests.get(api_url,headers=headers)

    # Check if the API call was successful (status code 200)
    if response.status_code == 200:
        # Extract show type from the API response (Assuming the show type is in the 'type' field of the response JSON)
        show_type =json.loads(response.text)['result'][0]['show_type']
        print(show_id,show_type)
        return show_type
    else:
        # Return None if the API call fails or encounters an error
        print(show_id,"error")
        return "error"
    

# Apply the get_show_type function to DataFrame C to fetch show types
res['type'] = res['show_id'].apply(get_show_type)

res.to_csv('english_diff.csv',index=False)
# Find rows in B that are not in A based on 'show id'
# merged_df = pd.merge(hindi_revenue_df, hindi_api_df, on='show_id', how='left', indicator=True)
# # print(merged_df)clear

# # merged_df.to_csv('merged.csv',index=False)
# hindi_res =merged_df.loc[merged_df['_merge'] == 'left_only', ['show_id', 'Show Title']]
# hindi_res.drop('_merge', axis=1, inplace=True)
# hindi_res.to_csv('hindi_result.csv',index=False)

