import pandas as pd
import random
from string import Template
import requests


IFRAME_TEMPLATE = Template("""
    <div class="videoBox">
    <h2>${vidname}</h2>
    <iframe src="https://www.youtube.com/embed/${youtube_id}?start=${start_time}&end=${end_time}&controls=0" width="853" height="480" frameborder="0" allowfullscreen></iframe>""")

OPTIONS_TEMPLATE_ANSWERS=Template("""<div>
                                        <input type="${type}" id="${opt_id}" name="${name}" value="${value}" ${requirement} />
                                        <label for="${opt_id}" class="${type}"><span>${value}</span></label>
                                      </div>
                                  """)


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

    hed = """<!DOCTYPE html>
    <html lang="en">
    <link rel="preconnect" href="https://fonts.gstatic.com">
    <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700" rel="stylesheet">
    <link rel="stylesheet" href="/static/stylesheets/styles_cool.css">
    
    <head>
    <meta charset="UTF-8">

        <title>TrustworthinessFormIAnswers</title>
    </head>
    <body>
    <div class="testbox">"""

    form_def = """<form action="/end" method="post" class="videosForm">
            <div class="banner">
              <h1>Video Annotations</h1>
            </div>
        """

    #Add hidden fields to save user info:
    form_def+="""<input type="hidden" id="gender" name="gender" value="{gender}"/>""".format(gender=gender)
    form_def += """<input type="hidden" id="studies" name="studies" value="{studies}"/>""".format(studies=studies)
    form_def += """<input type="hidden" id="age" name="age" value="{age}"/>""".format(age=age)
    form_def += """<input type="hidden" id="nationality" name="nationality" value="{nationality}"/>""".format(nationality=nationality)
    form_def += """<input type="hidden" id="race" name="race" value="{race}"/>""".format(race=race)

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


def is_url_ok(url):
    return 200 == requests.head(url).status_code


def html_radiobutton(question):
    header_radioButtion = """<div class="question">
           <p>{question}*</p>
            <label></label>
           <div class="question-answer">
              """.format(question=question)
    end_radioButton = """</div></div>"""
    return header_radioButtion, end_radioButton




def template_videos_onfly(vid, start, end, vidName, videoID):
    youtube_url = 'https://www.youtube.com/embed/' + vid +"?start="+start+"&end="+end
    video_avail = True
    if (is_url_ok(youtube_url)):
        ############## START WITH VIDEOS & QUESTIONS/OPTIONS...
        id_video = """<input type="hidden" id="{vidName}" name="{vidName}" value="{videoID}"/>""".format(vidName=vidName,videoID=videoID)
        iframe = IFRAME_TEMPLATE.substitute(youtube_id=vid, start_time=start, end_time=end, vidname=vidName)
        finalTemplate = id_video + iframe
        # Load csv:
        df_questions = pd.read_csv("static/extraInfo/questions.csv", sep=";", header=0)

        # Option to randomize questions
        for i, row in df_questions.iterrows():
            options = row["Options"].replace("[", "").replace("]", "").split(",")
            #question = """<p>{id}</p>""".format(id=row["Text"])
            header_radioButtions, end_radioButtons = html_radiobutton(row["Text"])


            finalTemplate += header_radioButtions
            if (row["TypeQuestion"] == "Option"):
                type_opt = "radio"

            elif (row["TypeQuestion"] == "MultiOption"): #Buscar checkbox
                type_opt = "checkbox"
            else:
                type_opt = "checkbox"

            #OPTIONS
            n = 0
            for single_option in options:
                if(n==0 and type_opt=="radio"):
                    require = "required"
                else:
                    require = ""
                finalTemplate += OPTIONS_TEMPLATE_ANSWERS.substitute(type=type_opt,opt_id=row["ID"]+vidName+single_option,
                                                                       value=single_option, requirement=require, name=row["ID"]+vidName)
                n+=1
            finalTemplate+=end_radioButtons
        #End video.
        finalTemplate += """</div>"""


    else:
        video_avail = False
        finalTemplate = """<h2>Youtube video {id} <strong>does not exist</strong></h2>""".format(id=vid)

    return finalTemplate
