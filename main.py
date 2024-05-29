from datetime import datetime
import requests
import json
import pandas as pd
import pywhatkit
import schedule


def fetch_data(session_cookie, year):

    # Generate url
    url = f'https://adventofcode.com/{year}/leaderboard/private/view/2097161.json'
    
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

    # Load prior data frame
    df_prior = pd.read_csv(f"leaderboard_{year}.csv", index_col=0)

    # Override csv with current data
    df.to_csv(f"leaderboard_{year}.csv", sep=',', header=True)

    return df, df_prior


def gen_msg(df, df_prior, year):

    # Build the message string
    message = f'```MESSAGE FROM AOC MONITOR ({year})\n\n'

    # Get length of longest member name
    max_name = max([len(name) for name in df.index])

    # Generate string to hold leaderboard information
    leaderboard = str()


    # Iterate over all members in df
    for member in df.sort_values('Score', ascending=False).index:

        # Formatting: Generate number of spaces to align names
        spaces_name = (max_name - len(member) + 1)*' '

        # Formatting: Generate number of spaces to align stars
        stars_member = df.loc[df.index == member, 'Stars'].values[0]
        spaces_star = ' '
        if stars_member < 10:
            spaces_star = '  '

        # Formatting: Generate number of spaces to align scores
        score_member = df.loc[df.index == member, 'Score'].values[0]
        spaces_score = ' '
        if score_member < 10:
            spaces_score = '  '
        
        # Add information to leaderboard string
        leaderboard = leaderboard + f'{member}:{spaces_name}'\
                                    f'⭐{spaces_star}{stars_member}'\
                                    f'{spaces_score}({score_member})\n'


    # Check if number of memebers changed
    if len(df) != len(df_prior):

        # Complete message string
        message = message + 'Number of members has changed!```'

    else:
        # Check if there is a change in earned stars
        if sum(df_prior.Stars != df.Stars) == 0:

            # Exit if there is no change
            message = 'No change'
            # sys.exit()
        
        else:
            
            # If there is a change, iterate over respective members
            for member in df.index[df_prior.Stars != df.Stars]:
            
                # Determine how many stars have been earned
                earned = (df.loc[df.index == member, 'Stars'].values[0] -
                        df_prior.loc[df_prior.index == member, 'Stars'].values[0])
                
                # Account for correct writing
                if abs(earned) == 1:
                    word_star = 'star'
                else:
                    word_star = 'stars'
                
                # Add member information to message string
                message = message + f'Congratulations {member}!\n' \
                                    f'You earned {earned} {word_star} ⭐\n\n'
            
            # Add leaderboard to end of message
            message = message + f'Current leaderboard:\n{leaderboard[:-1]}```'

    return message


def main():

    # Set session cookie
    session_cookie = open('session_cookie.txt').read()

    # Set event
    year = 2015

    # # Fetch input data
    # data = fetch_data(session_cookie, year)

    # # Store the JSON data in a file
    # with open(f"leaderboard_{year}.json", "w") as file:
    #     json.dump(data, file)

    # Retrieve JSON data from the file
    with open(f"leaderboard_{year}.json", "r") as file:
        data = json.load(file)

    # Generate data frames
    df, df_prior = gen_dfs(data, year)
    # df = gen_dfs(data, year)

    # # Modify df for testing purposes
    # df.loc['NewMember'] = [25, 50]
    df.iloc[0,0] = 100
    # df.iloc[3,0] = 100

    # Generate message
    message = gen_msg(df, df_prior, year)

    print(datetime.now(), message, sep='\n')

    # Send test message
    h = int(datetime.now().strftime('%H'))
    m = int(datetime.now().strftime('%M'))
    print('sending message...')
    pywhatkit.sendwhatmsg("+4917651995472", message=message, time_hour=h, time_min=m+1, tab_close=True)
    print('message sent!')

# Run main method
if __name__ == '__main__':

    # Set schedule
    schedule.every(3).minutes.do(main)
    
    # Run schedule
    while True:
        schedule.run_pending()

# Send WhatsApp message
# pywhatkit.sendwhatmsg_to_group_instantly("Gcoef0k7uRy8rhtMNEqfKH", message=message, tab_close=True)