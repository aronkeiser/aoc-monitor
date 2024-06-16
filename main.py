import requests
import pandas as pd
import json
import schedule
from datetime import datetime
import os
import sys
import types

# Create a mock module for pyautogui
mock = types.ModuleType("pyautogui")
mock.click = lambda *args, **kwargs: None
mock.hotkey = lambda *args, **kwargs: None
mock.press = lambda *args, **kwargs: None
mock.size = lambda: (1920, 1080)  # Return a default screen size
mock.typewrite = lambda *args, **kwargs: None

sys.modules["pyautogui"] = mock

# Now import pywhatkit after the mock is set up
import pywhatkit

def fetch_data(session_cookie, leaderboard_id, year):

    # Generate url
    url = f'https://adventofcode.com/{year}/leaderboard/private/view/{leaderboard_id}.json'
    
    # Generate header
    headers = {'Cookie': f'session={session_cookie}'}
    
    # Run request
    response = requests.get(url, headers=headers)
    
    # Check if request ran successful return response data
    if response.status_code == 200:        
        return response.json()

    else:
        # Error handling
        print(f'Failed to fetch leaderboard information. Status code: {response.status_code}')


def gen_dfs(data, year):

    # Initialize lists to hold data
    members, stars, local_score = ([] for i in range(3))

    # Query json file and append to lists
    for member in data['members']:

        # Get member names
        members.append(data['members'][f'{member}']['name'])

        # Get sum of earned stars
        stars.append(data['members'][f'{member}']['stars'])

        # Get local score
        local_score.append(data['members'][f'{member}']['local_score'])

    # Generate new data frame
    df = pd.DataFrame()
    df['Name']  = members
    df['Stars'] = stars
    df['Score'] = local_score

    # Sort data frame
    df.set_index('Name', inplace=True)
    df.sort_index(inplace=True)

    # Get file path
    file_path = os.path.join(os.getenv('GITHUB_WORKSPACE', ''), 'leaderboards', f'leaderboard_{year}.csv')
    print(file_path)

    # Load prior data frame
    try:
        e = 0
        df_prior = pd.read_csv(file_path, index_col=0)
        return df, df_prior, e

    # Return new df as prior if non-existent
    except FileNotFoundError as e:
        return df, df, e
    
    # Override csv with current data
    finally:
        df.to_csv(file_path, sep=',', header=True)


def gen_msg(df, df_prior, year):

    # Build the message string
    message = f'_Message from AOC Monitor ({year})_\n\n'

    # Get length of longest member name
    max_name = max([len(name) for name in df.index])
    spaces_name_header = ' '*(max_name-4)
    spaces_name_dash = '-'*(max_name-2)

    # Generate string to hold leaderboard information
    leaderboard = str(f'Name{spaces_name_header}Stars  Score\n'\
                      f'{spaces_name_dash}--------------\n')

    # Iterate over all members in df
    for member in df.sort_values(['Score','Stars'], ascending=[False, False]).index:

        # Formatting: Generate number of spaces to align names
        spaces_name = (max_name - len(member) + 1)*' '

        # Formatting: Generate number of spaces to align stars
        stars_member = df.loc[df.index == member, 'Stars'].values[0]
        spaces_star = '    '[:-len(str(stars_member))]

        # Formatting: Generate number of spaces to align scores
        score_member = df.loc[df.index == member, 'Score'].values[0]
        spaces_score = '       '[:-len(str(score_member))]
        
        # Add information to leaderboard string
        leaderboard = leaderboard + f'{member}{spaces_name}'\
                                    f'{spaces_star}{stars_member}'\
                                    f'{spaces_score}{score_member}\n'

    # Check if number of memebers changed
    if len(df) != len(df_prior):

        # Complete message string
        message = message + 'Number of members has changed!'

    else:
        # Check if there is a change in earned stars
        if sum(df_prior.Stars != df.Stars) == 0:
            message = 'No change'
        
        else:
            
            # If there is a change, iterate over respective members
            for member in df.index[df_prior.Stars != df.Stars]:
            
                # Determine how many stars have been earned
                earned = (df.loc[df.index == member, 'Stars'].values[0] -
                          df_prior.loc[df_prior.index == member, 'Stars'].values[0])
                
                # Account for correct writing
                if abs(earned) == 1:
                    word_spelling = 'star'
                else:
                    word_spelling = 'stars'
                
                # Add member information to message string
                message = message + f'Congratulations *{member}*!\n' \
                                    f'You earned *{earned} {word_spelling}*.\n\n'
            
            # Add leaderboard to end of message
            message = message + f'Current leaderboard:\n\n```{leaderboard[:-1]}``` '

    return message


def main():

    # # Load connection details
    # static = pd.read_csv('connect.csv', index_col=0)
    
    # Set session cookie
    # session_cookie = static.loc['session_cookie'].values[0]
    session_cookie = os.environ.get('SESSION_COOKIE')

    # Set WhatsApp group chat id
    # whatsapp_gc_id = static.loc['whatsapp_gc_id'].values[0]
    whatsapp_gc_id = os.environ.get('WHATSAPP_GC_ID')

    # Set leaderboard id
    # leaderboard_id = static.loc['leaderboard_id'].values[0]
    leaderboard_id = os.environ.get('LEADERBOARD_ID')

    # Generate list of all available events
    years = list(range(2015, datetime.today().year))

    if datetime.today().month == 12:
        years.append(datetime.today().year)

    # Set no change counter to 0
    no_change = 0

    # Iterate over each year
    for year in [years[0]]:

        # Fetch input data
        data = fetch_data(session_cookie, leaderboard_id, year)

        # # Store the JSON data in a file (testing)
        # with open(f'leaderboards/leaderboard_{year}.json', "w") as file:
        #     json.dump(data, file)

        # # Retrieve JSON data from the file (testing)
        # with open(f'leaderboards/leaderboard_{year}.json', "r") as file:
        #     data = json.load(file)

        # Generate data frames
        df, df_prior, e = gen_dfs(data, year)

        # # Modify df (testing)
        # df.loc['NewMember'] = [25, 50]
        df.iloc[0,0] = 13

        # Generate message
        message = gen_msg(df, df_prior, year)

        # Feedback to terminal when new event is available
        if (message == 'No change') & (e != 0):
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f'Generating new leaderboard for {year}!')
        
        # Feedback to terminal if no change
        elif message == 'No change':
            no_change += 1
        
        # Send WhatsApp message for any change
        else:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f'Change detected in {year} leaderboard! Sending message...')
            pywhatkit.sendwhatmsg_to_group_instantly(whatsapp_gc_id, message=message, wait_time=30, tab_close=True)

    # If all years show now change, only send message once
    if no_change == len(years):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'No change')
    

# # Run main method
# if __name__ == '__main__':

#     # Set schedule
#     schedule.every(30).minutes.do(main)
    
#     # Run schedule
#     while True:
#         schedule.run_pending()

main()