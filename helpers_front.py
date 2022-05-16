import pandas as pd
import random
from string import Template
import requests
import numpy as np
import pickle


IFRAME_TEMPLATE = Template("""
    <div class="videoBox">
    <h2>${vidname}</h2>
    <iframe id="${vidname}iframe" src="https://www.youtube.com/embed/${youtube_id}?start=${start_time}&end=${end_time}&controls=0" width="853" height="480" frameborder="0" allowfullscreen></iframe>""")

OPTIONS_TEMPLATE_ANSWERS=Template("""<div>
                                        <input type="${type}" id="${opt_id}" name="${name}" value="${value}" ${requirement} ${checked}/>
                                        <label for="${opt_id}" class="${type}"><span>${value}</span></label>
                                      </div>
                                  """)

OTHER_TEMPLATE_OPTION=Template("""<div>
            <textarea rows = "2" cols = "60" id="${opt_id}" name="${name}" placeholder="If you selected 'Other' option, enter details here ... "></textarea></div>""")

DEFAULT_CHECKED_OPTIONS = ["0 (Nothing)", "Neutral", "Yes", "Other"]







def get_random_videos(df_videos, n_videos=10):
    selected_videos_df = pd.DataFrame([], columns=df_videos.columns)
    videos_ids = list(df_videos["vid"].unique())

    if(len(videos_ids)<n_videos):
        n_videos = len(videos_ids)
    selected_videos = random.sample(videos_ids, n_videos)
    #Get URLS/dataframe to iterate later:
    for vid in selected_videos:
        #search for all options and select 1 randomly:
        df_subvids = df_videos.loc[df_videos["vid"]==vid]
        subindex = random.randint(0,len(df_subvids)-1)
        selected_videos_df = selected_videos_df.append(df_subvids.iloc[subindex])
    return selected_videos_df

def get_random_videos_perEmotion(df_videos, n_videos=10):
    #Select random emotion:
    list_emotions_OMG = [0,1,2,3,4,5] #0- Anger; 1-Disgust; 2-Fear; 3-Happy; 4-Neutral; 5-Sad; 6-Surprise (REMOVED SURPRISE SINCE JUST 1 SINGLE VIDEO)

    random_emot = get_random_strategies(list_emotions_OMG)#list_emotions_OMG[random.randint(0, len(list_emotions_OMG) - 1)]
    videosWithSameEmotion = df_videos.loc[df_videos["EmotionMaxVote"]==random_emot]

    # Select random videos from DF OF EMOTIONS
    selected_videos_df = get_random_videos(videosWithSameEmotion, n_videos=n_videos)
    return selected_videos_df

def get_random_strategies(list2select, listProbabilities=[]):
    if(len(listProbabilities)<=0): #Uniform probabilities -> all samples have the same probability to be chosen
        random_sample = list2select[random.randint(0, len(list2select) - 1)]
    else:
        # Select sample with non-uniform probabilities; different samples/groups have different probabilities indicated in listProbabilities to be selected
        # ** Necessary same order in list2select & listProbabilities
        new_list_prob = []
        for i in range(len(listProbabilities)):
            if(i==0):
                new_list_prob.append(listProbabilities[i]*100)
            else:
                new_list_prob.append((listProbabilities[i-1]+listProbabilities[i])*100)
        random_number = random.randint(0, 100)
        random_sample = -1
        #Check in which range it goes:
        for i in range(len(new_list_prob)):
            if(random_number<new_list_prob[i]):
                random_sample = list2select[i]
                break
    return random_sample


def create_probability_table():
    #MODIFY PROB_TABLE:
    df_labels = pd.read_csv("static/extraInfo/videos.csv", sep=",", header=0)
    prob_matrix = np.zeros((8, 7))
    valence_ranges = [-0.4, -0.2, 0, 0.2, 0.4, 0.6, 1]  # last steps bigger to collapse ex
    arousal_ranges = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1]
    last_valence = -1
    last_arousal = 0
    for valence_index in range(0,
                               len(valence_ranges)):  # As not enough samples in some cases, we collapse some extreme categories
        valence_value = valence_ranges[valence_index]
        for arousal_index in range(0, len(arousal_ranges)):
            arousal_value = arousal_ranges[arousal_index]
            videos_per_square = df_labels.loc[
                (df_labels['valence'] > last_valence) & (df_labels['valence'] <= valence_value) & (
                            df_labels['arousal'] > last_arousal) & (df_labels['arousal'] <= arousal_value)]
            # Add probabilities per square:
            prob_matrix[len(arousal_ranges) - arousal_index - 1, valence_index] = np.ceil(
                100 * len(videos_per_square) / len(df_labels))
            last_arousal = arousal_value
        last_valence = valence_value

    # Convert probs in ranges:
    last_val = 0
    for valence_index in range(0,
                               len(valence_ranges)):  # As not enough samples in some cases, we collapse some extreme categories
        for arousal_index in range(0, len(arousal_ranges)):
            prob_matrix[arousal_index, valence_index] += last_val
            last_val = prob_matrix[arousal_index, valence_index]
    print("NEW MATRIX: ", prob_matrix)
    #GENERATED MATRIX:
    with open('static/extraInfo/videosProbMatrix.pkl', 'wb') as f:
        pickle.dump(prob_matrix, f)






def get_random_VA_videos_OMG(df_videos,  n_videos=10):
    valence_ranges = [-0.4, -0.2, 0, 0.2, 0.4, 0.6, 1]  # last steps bigger to collapse ex
    arousal_ranges = [1, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]
    with open('static/extraInfo/videosProbMatrix.pkl', 'rb') as f:
        prob_matrix = pickle.load(f)
    random_number = random.randint(0, np.max(np.max(prob_matrix))) #Random number to select the V/A box
    print("RN: ", str(random_number))
    last_value = 0
    found = False
    #Get arousal&valence indexes:
    for valence_index in range(0,len(valence_ranges)):  # As not enough samples in some cases, we collapse some extreme categories
        if(found):
            valence_index-=1
            break
        for arousal_index in range(0, len(arousal_ranges)):
            #Look for value
            if(last_value<=random_number and prob_matrix[arousal_index,valence_index]>random_number):
                #Get index of valence/arousal:
                found=True
                break
            last_value = prob_matrix[arousal_index, valence_index]

    videosSameArousalValence = get_VA_videos(arousal_ranges, valence_ranges, arousal_index, valence_index, df_videos)

    if(len(videosSameArousalValence)>=n_videos):
        selected_videos_df = get_random_videos(videosSameArousalValence, n_videos=n_videos)
    else:
        #Start to check other squares around & repeat:
        selected_videos_df = get_random_videos(videosSameArousalValence, n_videos=len(videosSameArousalValence))
        videos_counter = (len(selected_videos_df))
        attempts = 0
        n_times = 1
        while(videos_counter<n_videos):
            #do recursive selections:
            if(attempts==0): #Check square to the rigth (+1 valence, same arousal)
                new_arousal_index = arousal_index
                new_valence_index = valence_index + 1*n_times
            elif(attempts==1):#Check square to the left (-1 valence, same arousal)
                new_arousal_index = arousal_index
                new_valence_index = valence_index - 1*n_times
            elif (attempts == 2):  # Check square below (same valence, -1 arousal)
                new_arousal_index = arousal_index - 1*n_times
                new_valence_index = valence_index
            elif (attempts == 3):  # Check square up (same valence, +1 arousal)
                new_arousal_index = arousal_index + 1*n_times
                new_valence_index = valence_index
            elif (attempts == 4): # Check square right-down (+1 valence, -1 arousal)
                new_arousal_index = arousal_index - 1*n_times
                new_valence_index = valence_index + 1*n_times
            elif (attempts == 5):  # Check square left-down (11 valence, +1 arousal)
                new_arousal_index = arousal_index + 1*n_times
                new_valence_index = valence_index - 1*n_times
            elif (attempts == 6):  # Check square right-up (+1 valence, +1 arousal)
                new_arousal_index = arousal_index + 1*n_times
                new_valence_index = valence_index + 1*n_times
            elif (attempts == 7):  # Check square left-up (-1 valence, +1 arousal)
                new_arousal_index = arousal_index + 1*n_times
                new_valence_index = valence_index - 1*n_times
            else:
                print("Reset loop (xN steps neighbours)")
                n_times+=1
                new_arousal_index = arousal_index
                new_valence_index = valence_index + 1*n_times
                attempts=0

            if(new_arousal_index<0 or new_valence_index<0 or new_valence_index>6 or new_arousal_index>7):
                attempts += 1
                continue

            try:
                sub_selected_videos_df = get_VA_videos(arousal_ranges, valence_ranges, new_arousal_index, new_valence_index, df_videos)
                if(len(sub_selected_videos_df)>0):
                    #Append
                    selected_videos_df_aux = get_random_videos(sub_selected_videos_df, n_videos=n_videos-(len(selected_videos_df)))
                    #Check that vid is different
                    for i, row in selected_videos_df_aux.iterrows():
                        if(not row["vid"] in selected_videos_df["vid"].values):
                            selected_videos_df = selected_videos_df.append(pd.DataFrame([row], columns=selected_videos_df.columns))


                    #selected_videos_df = selected_videos_df.append(selected_videos_df_aux, ignore_index = True)
                    videos_counter = len(selected_videos_df)
            except IndexError:
                pass
            finally:
                attempts+=1
    print(selected_videos_df)
    return selected_videos_df





def get_VA_videos(arousal_ranges, valence_ranges, arousal_index, valence_index, df_videos):
    selected_arousal = arousal_ranges[arousal_index]
    selected_valence = valence_ranges[valence_index]
    if (selected_valence == -0.4):
        last_valence = -1
    else:
        last_valence = valence_ranges[valence_index - 1]

    if (selected_arousal == 0.2):
        last_arousal = 0
    else:
        last_arousal = arousal_ranges[arousal_index + 1]

    videosSameArousalValence = df_videos.loc[
        (df_videos['valence'] > last_valence) & (df_videos['valence'] <= selected_valence) & (
                df_videos['arousal'] > last_arousal) & (df_videos['arousal'] <= selected_arousal)]
    return videosSameArousalValence




def create_header_HTML():
    hed = """<!DOCTYPE html>
       <html lang="en">
       <link rel="preconnect" href="https://fonts.gstatic.com">
       <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700" rel="stylesheet">
       <link rel="stylesheet" href="/static/stylesheets/styles_cool.css">

       <head>
       <meta charset="UTF-8">

           <title>TrustworthinessFormIAnswers</title>
           <script>
               function playme(vidName) {
               document.getElementById(vidName+"iframe").src = document.getElementById(vidName+"iframe").src;
               }
           </script>     
       </head>
       <body>
       <div class="testbox">"""
    return hed

def create_header_videos(annotatorID, gender, englishLevel, studies,age,nationality,race, timestamp):
    hed = create_header_HTML()


    form_def = """<form action="/end" method="post" class="videosForm">
            <div class="banner">
              <h1>Video Annotations</h1>
            </div>
        """

    #Add hidden fields to save user info:
    form_def += """<input type="hidden" id="annotatorID" name="annotatorID" value="{annotatorID}"/>""".format(annotatorID=annotatorID)
    form_def+="""<input type="hidden" id="gender" name="gender" value="{gender}"/>""".format(gender=gender)
    form_def += """<input type="hidden" id="englishLevel" name="englishLevel" value="{englishLevel}"/>""".format(englishLevel=englishLevel)
    form_def += """<input type="hidden" id="studies" name="studies" value="{studies}"/>""".format(studies=studies)
    form_def += """<input type="hidden" id="age" name="age" value="{age}"/>""".format(age=age)
    form_def += """<input type="hidden" id="nationality" name="nationality" value="{nationality}"/>""".format(nationality=nationality)
    form_def += """<input type="hidden" id="race" name="race" value="{race}"/>""".format(race=race)
    form_def += """<input type="hidden" id="timestamp" name="timestamp" value="{timestamp}"/>""".format(timestamp=timestamp)

    header = hed+form_def
    return header


def create_end_videos():
    end_html = """<div class="btn-block">
                    <button type="submit"> Continue >> </button>
                  </div>
            </form>
          </div>
        </body>
        </html>"""
    return end_html



def try_site(url):
    new_url = url
    pattern = '"playabilityStatus":{"status":"ERROR"' #,"reason":"Video unavailable
    pattern_private = '"playabilityStatus":{"status":"LOGIN_REQUIRED","messages":["Ini video peribadi.'
    request = requests.get(url, allow_redirects=False)
    if (not(pattern in request.text) and (not (pattern_private in request.text))and request.status_code == 200):
        return True, new_url
    elif(pattern in request.text):
        print("Error in ", url)
        return False, new_url
    elif(request.status_code == 303):
        newrequest = requests.get(url, allow_redirects=True)
        new_url = newrequest.url
        return True, new_url
    else:
        return False, new_url


def html_radiobutton(question):
    header_radioButtion = """<div class="question">
           <p>{question} <span class="questionText">*</span></p>
            <label></label>
           <div class="question-answer">
              """.format(question=question)
    end_radioButton = """</div></div>"""
    return header_radioButtion, end_radioButton




def template_videos_onfly(df_questions, vid, start, end, vidName, videoID):
    id_video = """<input type="hidden" id="{vidName}" name="{vidName}" value="{videoID}"/>""".format(vidName=vidName,videoID=videoID)
    iframe = IFRAME_TEMPLATE.substitute(youtube_id=vid, start_time=start, end_time=end, vidname=vidName)
    #Add button to play again the video:
    button_html = """<button type="button" id="{vidName}button" onclick="playme('{vidName}')">Play Again</button>""".format(vidName=vidName)

    finalTemplate = id_video + iframe +button_html

    n_quest = 0
    # Option to randomize questions
    for i, row in df_questions.iterrows():
        options = row["Options"].replace("[", "").replace("]", "").split(",")
        #question = """<p>{id}</p>""".format(id=row["Text"])
        header_radioButtions, end_radioButtons = html_radiobutton(str(n_quest)+". " +row["Text"])


        finalTemplate += header_radioButtions
        if (row["TypeQuestion"] == "Option"):
            type_opt = "radio"

        elif (row["TypeQuestion"] == "MultiOption"): #Buscar checkbox
            type_opt = "checkbox"
        else:
            type_opt = "checkbox"

        #OPTIONS
        n_option = 0
        for single_option in options:
            if(n_option==0 and type_opt=="radio"):
                require = "required"
            else:
                require = ""

            if(single_option in DEFAULT_CHECKED_OPTIONS):
                checked = "checked"
            else:
                checked = ""
            finalTemplate += OPTIONS_TEMPLATE_ANSWERS.substitute(type=type_opt,opt_id=row["ID"]+vidName+single_option,
                                                                   value=single_option, requirement=require, name=row["ID"]+vidName, checked=checked)
            n_option+=1
        finalTemplate+=end_radioButtons
        n_quest+=1
    #End video.
    #For fill in
    finalTemplate+= OTHER_TEMPLATE_OPTION.substitute(opt_id="TextArea"+vidName, name="TextArea"+vidName)
    finalTemplate += """</div>"""
    return finalTemplate







#################################### CHECK ANNOTATIONS #######################################
