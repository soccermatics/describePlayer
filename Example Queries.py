#Note: The openai-python library support for Azure OpenAI is in preview.
import openai
import pandas as pd
import passwords

openai.api_type = "azure"
openai.api_base = passwords.GPT_BASE
openai.api_version = passwords.GPT_VERSION
openai.api_key = passwords.GPT_KEY

def describe_level(z_score):
    if z_score >= 1.5:
        description = "outstanding"
    elif z_score >= 1:
        description = "excellent"
    elif z_score >= 0.5:
        description = "good"
    elif z_score >= -0.5:
        description = "average"
    elif z_score >= -1:
        description = "below average"
    else:
        description = "poor"
   
    return description


#%%###########################################################################################
# First we set up the bot by telling it who it is.

# Set up messages 
messages = [
    {"role": "system", "content": "You are a UK-based football scout. \
            You provide succinct and to the point summaries of football players \
            based on data. You talk in footballing terms about data. \
            You use the information given to you from the data and answers \
            to earlier user/assistant pairs to give summaries of players. \
            Your current job is to assess players in the striker position." },
        {"role": "user", "content": "Do you refer to the game you are an \
         expert in as soccer or football?"},
        {"role": "assistant", "content": "I refer to the game as football. \
         When I say football, I don't mean American football, I mean what \
         Americans call soccer. But I always talk about football, as people \
         do in the United Kingdom."}]


    
# Read in the descriptions of the activities
# Set to True to read in descriptions
if False:
    df1=pd.read_csv('Involvement.csv')
    df2=pd.read_csv('Poaching.csv')
    df=df1.append(df2)

    for i,query in df.iterrows():
        user={"role": "user", "content": query['user']}
        messages = messages + [user]
        assistant={"role": "assistant", "content": query['assistant']}
        messages = messages + [assistant]    


# Here is the player to be ranked. We have already measured their involvement 
# and poaching relevant to other players.
name='Smith'
involvement = 1.2
poaching = 1.4

player_description = "When it comes to involvement " + name + " is " + describe_level(involvement) +'.'
player_description = player_description + "When it comes to poaching " + name + " is " + describe_level(poaching)+'.'

start_prompt ="Below is a description of a player's involvement snd their poaching skills':\n\n"
end_prompt = "\n Use what you know about involvement and poaching to speculate (using at most two sentences) on the role the player might take in a team."
end_prompt = "\n Use the data provided to summarise the player in two sentences."
end_prompt = "\n Explain how the player's involvement in the match is calculated."
end_prompt = "\n Does the player get involved in the game and if not, should we be worried?"

                                                                                         
# Read in the descriptions up to date
try:
    current_df = pd.read_excel('Descriptions.xlsx')
    
    for number_provided,query in current_df.iterrows():
        previous_description = query['user']
        the_prompt=start_prompt + previous_description + end_prompt
        user={"role": "user", "content": the_prompt}
        messages = messages + [user]
        assistant={"role": "assistant", "content": query['assitant']}
        messages = messages + [assistant]
        
except:
    current_df = pd.DataFrame()
    print("No descriptions file")


#Now ask about current player

the_prompt=start_prompt + player_description + end_prompt
user={"role": "user", "content": the_prompt}
messages = messages + [user]

# Now the main query.

print(messages)

response = openai.ChatCompletion.create(
        engine="TwelveChatGPT", # engine = "deployment_name".
        messages=messages
)

GPT_describe=response['choices'][0]['message']['content']
print(GPT_describe)
data = pd.DataFrame({"user": player_description, "assistant": GPT_describe}, index=[0])
current_df = current_df.append(data) 
    
current_df.to_excel('Descriptions GPT.xlsx')  

