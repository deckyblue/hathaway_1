"""
This module includes functions to load in MEDPC data and outputs a dataframe. 

Authors: Brett Hathaway & Dexter Kim 
"""

print("I am being executed!")

#main imports 
import os
import pandas as pd
import numpy as np

# plotting imports 
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# stats imports 
import scipy.stats as stats

#the following line prevents pandas from giving unecessary errors 
pd.options.mode.chained_assignment = None

#---------------------------------------------------------------#

#test 
def square(num): 
    return num^2

#---------------------------------------------------------------#

def load_data(fnames): ##fnames is an argument, and a list of strings (file names) 
    for i,file in enumerate(fnames): ##i means index (0, 1, etc.) // file is the file name (str)
##enumerate takes a list, and makes a new list where the elements are index + something (eg 0, 'BH07_raw_free_S29-30.xlsx')
        if i == 0:
            df = pd.read_excel(fnames[i]) #load in the first file from the 'file_names' list
        else:
            df2 = pd.read_excel(fnames[i]) #load in subsequent file
    #i > 0, and fnames[i] refers to the ith element of the list, fnames
            df = df.append(df2, ignore_index = True) #append it to the first file
    return df

def check_sessions(df): ##checks that the 'Session' column has correct, and non-missing session numbers
    pd.set_option('display.max_rows', None) ##otherwise it will ... the middle rows (only give the head and tail)
    print(df.groupby(['Subject','StartDate','Session'])['Trial'].max())
    pd.set_option('display.max_rows',df.Subject.max()) ##this sets the number of displayed rows to the number of subjects
    
def drop_sessions(df, session_nums):
    'Takes in a list of session numbers, and removes the data from specified session numbers'
    for s in session_nums:
        drop_sess = list(df.loc[df['Session'] == s].index)
        df.drop(drop_sess, inplace = True)
        df.reset_index(inplace = True)
    return None ##could replace with check_sessions(df)
    
#---------------------------------------------------------------#

def get_choices(df):
    configA = np.array([1, 4, 0, 2, 3]) #this is the order for version A - i.e., hole 1 corresponds to P1
    configB = np.array([4, 1, 0, 3, 2]) #this is the order for version B - i.e., hole 1 corresponds to P4

    #I took the following code from someone else, so honestly I'm not entirely sure how it works haha
    #the important thing is that it uses the configurations above to assign the correct option, 
    #based on whether the MSN name contains 'A' or 'B'
    df['option'] = df['MSN'].str.contains("B").values*configB[df['Chosen'].astype('int').ravel()-1].astype('int') + \
        df['MSN'].str.contains("A").values*configA[df['Chosen'].astype('int').ravel()-1].astype('int')
    
    ###I can just take your word for it right? haha
    ####Yes

    #the above code changes any zero in the chosen column to a three in the option column - don't need to know why
    #so we need to fix that (zeros represent either a premature response or an omission)
    for i in range(len(df)): ##range gives me a list from 0 to the len(df), which should be all the indices
        if df['Chosen'][i] == 0: ###can we say this in English? 
            ##the same as df.at
            ##if the index of the 'Chosen' column gets 0 --> option equals 0 
            df['option'][i] = 0 
    return df    

#---------------------------------------------------------------#

def get_sum_choice(num, df): ##arguments: session number, dataframe
    #first we create a df with only data from the given session number
    df1 = df.loc[df['Session'] == num]

###dataframe.loc accesses a group of columns/rows? ####Yes
###if so, is df.loc accessing all rows where 'Session' gets num? ####Yes

    #then we create a list of subject numbers, and sort them
    subs = df1.Subject.unique() ##list of unique subject numbers (1-32)
    subs.sort() ##and sort them
    #then we create a df called percentage, which has 4 columns --> P1 to P4, leading with the session number
    #i.e., if session number = 29, the columns will be 29P1, 29P2, 29P3, 29P4
    percentage = pd.DataFrame(columns=[str(num) + 'P1',str(num) + 'P2',str(num) + 'P3',str(num) + 'P4'])
    
##recall: you can add strings lol
###does pd.DataFrame create a dataframe? ####Yes

    for sub in subs: #for each subject 
        for i,column in enumerate(percentage.columns): #for each option 
###percentage.columns called the columns in percentage (object) --> produced enumerated list? couldn't check
##enumerate stores 2 different lists
##list for i [0,1,2,3] (columns)
##list for column [29P1, 29P2, etc...]
##first loop: i = 0, column = 29P1 
##we would go through this loop, 4 times, for each subject. (128 times)

            #this calculates the %choice (number of times that option is selected) divided by total number of choices,
            #multiplied by 100
            percentage.at[sub,column] = (len(df1.loc[(df1.option == i + 1) & ##P1 is 1 in the option column
                                            (df1.Subject == sub)]))/(len(df1.loc[(df1['option'] != 0) & 
                                                                                (df.Subject == sub)])) *100
    return percentage

#---------------------------------------------------------------#

def get_sum_choice_all(df):
    #create an empty list to store the sessions individually
    df_sess = []
    for num in np.sort(df['Session'].unique()): ##for each session number in list of session numbers 
        df_sess.append(get_sum_choice(num,df)) ##append the summary info from get_sum_choice to the above list ###appending side-to-side? ####just makes a list
    #then turn that list into a df
    ##recall, get_sum_choice outputs a dataframe

    df1 = pd.concat(df_sess, axis=1) ###appends the list of dataframes side by side
    #let's also calculate the risk score for each session - (P1 + P2) - (P3 + P4)
    for num in np.sort(df['Session'].unique()):
        df1['risk'+ str(num)] = df1[str(num)+'P1'] + df1[str(num)+'P2']- df1[str(num)+'P3'] - df1[str(num)+'P4']
        ##these are all names of columns 
        ##df1[str(num)+'P2'] is 29P2
    return df1

#---------------------------------------------------------------#

def get_premature(df_raw,df_sum):
    #add up the number of premature responses made by (each subject for each session)--> the group
    #save this information to a dataframe called prem_resp
    prem_resp = df_raw.groupby(['Subject', 'Session'],as_index=False)['Premature_Resp'].sum()

##prem_resp took the raw df, grouped by subject and session, and summed the premature responses --> made a df
    
    #calculate the number of initiated trials for each subject for each session 
    prem_resp['Trials'] = df_raw.groupby(['Subject','Session'],as_index=False)['Trial'].count()['Trial']
    ##makes a new column called 'Trials' which counts the # of trials initiated
    ##'Trial' is an existing column in the raw df (in the .xlsx file)
    ###why is there 2 'Trial'? #### just takes the trials - try a new cell 

    #calculate the premature percent by dividing # of premature responses by # of trials initiated, times 100    
    prem_resp['prem_percent'] = prem_resp['Premature_Resp']/prem_resp['Trials'] * 100
    ###can we say this in English? easy

    #add this information to the summary dataframe
    #the column name will be 'prem' + session number - i.e., prem29 for session 29
    for num in np.sort(df_raw['Session'].unique()): #for each session in the raw dataframe
        #for that session, extract the prem_percent column from prem_resp and add it to the summary dataframe
        #set the index as the subject number, so it matches the summary dataframe
        df_sum['prem' + str(num)] = prem_resp.loc[prem_resp['Session']==num].set_index('Subject')['prem_percent']
        ####locate session == num, set index to Subject (1-32), and call prem_percent column of prem_resp --> assign it to df_sum(yadayada)
    return df_sum

#---------------------------------------------------------------#

def get_latencies(df_raw,df_sum):
    #extract only completed trials (including non-completed trials will skew the mean, as the latency is zero for those trials)
    df_raw = df_raw.loc[df_raw['Chosen'] != 0] ##'Chosen' = 0 indicates a prem_response or omission
    #group by subject and session, then calculate the mean collect latency
    collect_lat = df_raw.groupby(['Subject','Session'],as_index=False)['Collect_Lat'].mean()
    #group by subject and session, then calculate the mean choice latency
    choice_lat = df_raw.groupby(['Subject','Session'],as_index=False)['Choice_Lat'].mean()
    
    #add this information to the summary dataframe - same method as used above for premature responding
    for num in np.sort(df_raw['Session'].unique()):
        df_sum['collect_lat' + str(num)] = collect_lat.loc[collect_lat['Session']==num].set_index('Subject')['Collect_Lat']
    for num in np.sort(df_raw['Session'].unique()):
        df_sum['choice_lat' + str(num)] = choice_lat.loc[choice_lat['Session']==num].set_index('Subject')['Choice_Lat']
        ###we're setting the index to subject, so why is ['Choice_Lat'] here?
    return df_sum

#---------------------------------------------------------------#

def get_omit(df_raw,df_sum):
    #group by subject and session and sum the 'omit' column
    omit = df_raw.groupby(['Subject','Session'],as_index=False)['Omit'].sum() 
##takes the raw dataframe, groups by subject and session, and takes the sum of the "Omit" column 
    #append this information to the summary dataframe
    for num in np.sort(df_raw['Session'].unique()): #gets all unique numbers in the session column
        df_sum['omit' + str(num)] = omit.loc[omit['Session']==num].set_index('Subject')['Omit']
    return df_sum

def get_trials(df_raw,df_sum):
    #group by subject and session and get the max number in the trial column
    trials = df_raw.groupby(['Subject','Session'],as_index=False)['Trial'].max()
    #append this information to the summary dataframe
    for num in np.sort(df_raw['Session'].unique()):
        df_sum['trial' + str(num)] = trials.loc[trials['Session']==num].set_index('Subject')['Trial']
    return df_sum

#---------------------------------------------------------------#

def get_summary_data(df_raw):
    df_raw = get_choices(df_raw)
    df_sum = get_sum_choice_all(df_raw)
    df_sum = get_latencies(df_raw,df_sum)
    df_sum = get_omit(df_raw,df_sum)
    df_sum = get_trials(df_raw,df_sum)
    df_sum = get_premature(df_raw,df_sum)
    return df_sum

#---------------------------------------------------------------#

def get_risk_status(df_sum, startsess, endsess):
    #get risk status from specified sessions
    #create lists for indexing based on risk status
    risky = []
    optimal = []
    startsess = 'risk' + str(startsess)
    endsess = 'risk' + str(endsess)
    #calculate the mean risk score from the specified sessions
    df_sum['mean_risk'] = df_sum.loc[:,startsess:endsess].mean(axis=1) ###did this create a 'mean_risk' column?
    for sub in df_sum.index: #for each subject
        if df_sum.at[sub,'mean_risk'] > 0: #if the mean risk for that subject is above zero
            df_sum.at[sub,'risk_status'] = 1 #assign them a risk status of 1
            optimal.append(sub) #and add them to the 'optimal' list
        elif df_sum.at[sub,'mean_risk'] < 0: #if the mean risk for that subject is below zero
            df_sum.at[sub,'risk_status'] = 2 #assign them a risk status of 2
            risky.append(sub) #and append them to the 'risky' list
    return df_sum, risky, optimal

#---------------------------------------------------------------#

def export_to_excel(df,groups,column_name = 'group',file_name = 'summary_data'):
    dfs = []
    for group in groups: #this splits the dataframe by group
        dfs.append(df.loc[group])
    for i,df in enumerate(dfs): #this assigns a number to the tg_status column - in this case, 0 for control, 1 for experimental
        df[column_name] = i ##i should be 0 and 1
    df_export = pd.concat(dfs) #this recombines the dataframes
    df_export.sort_index(inplace = True) #this sorts the subjects so they're in the right order after combining
    df_export.to_excel(file_name, index_label = 'Subject')
    
#------------------------------PLOTTING---------------------------------#
   
def get_group_means_sem(df_sum,groups, group_names):
    dfs = []
    #first split the dataframe based on experimental vs control
    for group in groups:
        dfs.append(df_sum.loc[group])
    #create two dataframes - one for the means, one for the SEM
    mean_scores = pd.DataFrame(columns=list(df_sum.columns))
    stderror = pd.DataFrame(columns=mean_scores.columns)
    #calculate the mean and standard errors, and store them in the above dataframes
    for column in mean_scores.columns:
        for i in range(len(groups)):
            mean_scores.at[i,column] = dfs[i][column].mean()
            stderror.at[i,column] = stats.sem(dfs[i][column])
    #rename the rows to be the group_names (i.e., transgene positive and transgene negative)   
    mean_scores.rename(index=group_names,inplace = True)
    stderror.rename(index=group_names, inplace = True)
    return mean_scores, stderror

def rgt_plot(variable,startsess,endsess,group_names,title,scores,sem, highlight = None, var_title = None):
    ##startsess and endsess allow us to clip the session data 
    if var_title == None:
        var_title = variable
    plt.rcParams.update({'font.size': 22})
    fig,ax = plt.subplots(figsize = (20,10))
    ax.set_ylabel(var_title)
    ax.set_xlabel('Session')
    ax.set_xlim(startsess,endsess)
    ax.set_title(title + ': ' + var_title + '\n' + 'Session ' + str(startsess) + '-' + str(endsess))
    ax.spines['right'].set_linewidth(0)
    ax.spines['top'].set_linewidth(0)
    ax.spines['left'].set_linewidth(2)
    ax.spines['bottom'].set_linewidth(2)
    ax.set_xlim(startsess-.1,endsess+.1)
    x=np.arange(startsess,endsess+1)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
   
    for i,group in enumerate(group_names):
        y = scores.loc[group,variable+str(startsess):variable+str(endsess)]
        plt.errorbar(x, y,
                     yerr = sem.loc[group,variable+str(startsess):variable+str(endsess)], 
                     label=group,linewidth=4, capsize = 8)
    if highlight != None:
        plt.axvline(highlight, 0, 1, color = 'gray', lw = 1)
        ax.fill_between([highlight,endsess], ax.get_ylim()[0], ax.get_ylim()[1], facecolor='gray', alpha=0.2)
    ax.legend()

def choice_bar_plot(startsess, endsess, scores, sem,cmap = 'default'):
    sess = list(range(startsess,endsess + 1))
    labels = ['P1','P2','P3','P4']
    df = pd.DataFrame()
    df1 = pd.DataFrame()
    if cmap == 'Paired':
        colors = [plt.cm.Paired(5),plt.cm.Paired(1),plt.cm.Paired(4),plt.cm.Paired(0)]
    if cmap == 'default':
        colors = [plt.cm.Set1(1),plt.cm.Set1(0)]
    for choice in labels:
        df[choice] = scores.loc[:, [col for col in scores.columns if choice in col 
                                    and int(col[:col.index('P')]) in sess]].mean(axis = 1)
        df1[choice] = sem.loc[:, [col for col in scores.columns if choice in col 
                                    and int(col[:col.index('P')]) in sess]].mean(axis = 1)
    ax = df.transpose().plot.bar(rot = 0, yerr = df1.transpose(), capsize = 8, figsize = (20,8))
    
    # Add some text for labels, title and custom x-axis tick labels, etc.
    plt.rcParams.update({'font.size': 18})
    ax.set_ylabel('% Choice', fontweight = 'bold', fontsize = 18)
    ax.set_title('P1-P4 Choice', fontweight = 'bold', fontsize = 22, pad = 20)
    ax.set_ylim(bottom = 0)
    ax.spines['right'].set_linewidth(0)
    ax.spines['top'].set_linewidth(0)
    ax.spines['left'].set_linewidth(2)
    ax.spines['bottom'].set_linewidth(2)
    ax.legend()
    