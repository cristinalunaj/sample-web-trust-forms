import pandas as pd
import random
from string import Template
import requests


IFRAME_TEMPLATE = Template("""
    <iframe src="https://www.youtube.com/embed/${youtube_id}?start=${start_time}&end=${end_time}&autoplay=1" width="853" height="480" frameborder="0" allowfullscreen></iframe>""")
OPTIONS_TEMPLATE_ANSWERS= Template("""<input type="${type}" id="${opt_id}" name="${name}" value="${value}" ${requirement}><label for="${opt_id}">${value}</label><br>""")




def get_random_videos(df_videos, n_videos=10):
    selected_videos_df = pd.DataFrame([], columns=df_videos.columns)
    videos_ids = list(df_videos["vid"].unique())

    selected_videos = random.sample(videos_ids, n_videos)
    #Get URLS/dataframe to iterate later:
    for vid in selected_videos:
        #search for all options and select 1 randomly:
        df_subvids = df_videos.loc[df_videos["vid"]==vid]
        subindex = random.randint(0,len(df_subvids)-1)
        selected_videos_df = selected_videos_df.append(df_subvids.iloc[subindex])
    return selected_videos_df



def create_header_videos(gender, studies,age,nationality,race):
    hed = """<h2>Trustworthiness Annotations</h2>"""

    form_def = """<form action="/end", method="post">"""
    #Add hidden fields to save user info:
    form_def+="""<input type="hidden" id="gender" name="gender" value="{gender}">""".format(gender=gender)
    form_def += """<input type="hidden" id="studies" name="studies" value="{studies}">""".format(studies=studies)
    form_def += """<input type="hidden" id="age" name="age" value="{age}">""".format(age=age)
    form_def += """<input type="hidden" id="nationality" name="nationality" value="{nationality}">""".format(nationality=nationality)
    form_def += """<input type="hidden" id="race" name="race" value="{race}">""".format(race=race)

    header = hed+form_def
    return header


def is_url_ok(url):
    return 200 == requests.head(url).status_code


def template_videos_onfly(vid, start, end, vidName, videoID):
    youtube_url = 'https://www.youtube.com/embed/' + vid +"?start="+start+"&end="+end
    video_avail = True
    if (is_url_ok(youtube_url)):
        ############## START WITH VIDEOS & QUESTIONS/OPTIONS...
        id_video = """<input type="hidden" id="{vidName}" name="{vidName}" value="{videoID}">""".format(vidName=vidName,videoID=videoID)
        iframe = IFRAME_TEMPLATE.substitute(youtube_id=vid, start_time=start, end_time=end)
        finalTemplate = id_video + iframe
        # Load csv:
        df_questions = pd.read_csv("static/extraInfo/questions.csv", sep=";", header=0)

        # Option to randomize questions
        for i, row in df_questions.iterrows():
            options = row["Options"].replace("[", "").replace("]", "").split(",")
            question = """<p>{id}</p>""".format(id=row["Text"])
            finalTemplate += question
            if (row["TypeQuestion"] == "Option"):
                type_opt = "radio"

            elif (row["TypeQuestion"] == "MultiOption"): #Buscar checkbox
                type_opt = "checkbox"
            else:
                type_opt = "checkbox"

            n=0
            for single_option in options:
                if(n==0 and type_opt=="radio"):
                    require = "required"
                else:
                    require = ""
                options_template = OPTIONS_TEMPLATE_ANSWERS.substitute(type=type_opt,opt_id=row["ID"] + "_" + single_option,
                                                                       value=single_option, requirement=require, name=row["ID"]+vidName)
                finalTemplate += options_template
                n+=1

    else:
        video_avail = False
        finalTemplate = """<h2>Youtube video {id} <strong>does not exist</strong></h2>""".format(id=vid)

    return finalTemplate
