from flask import Flask, render_template, request
import pandas as pd
import math
from CONFIG import *
from helpers_front import *
from helpers_back import *
import time

########## DATABASE CONNECTIONS
import os
import psycopg2

###############################
app = Flask(__name__)



#Description page
@app.route("/")
def index():
    return render_template("index.html", description=DESCRIPTION)

#Personal Data
@app.route("/personal_form", methods = ['POST', 'GET'])
def personalDataForm():
    # Render HTML with count variable
    return render_template("personalData.html")


#Video Form
@app.route("/video_form", methods = ['POST'])
def videoAnnotationForm():
    # Render HTML with count variable
    #Get data from user:
    if request.method == 'POST':
        #Access to fields by its name
        annotatorID = request.form['AnnotatorIDQ']
        gender = request.form['genderQ']
        englishLevel = request.form['englishLevelQ']
        studies = request.form['StudyQ']
        age = request.form['AgeQ']
        nationality = request.form['nationalityQ']
        race = request.form['RaceQ']
        currentTimestamp = int(time.time())

        #Get videos web:
        df_videos = pd.read_csv("static/extraInfo/videos.csv", sep=",", header=0)
        df_selected_videos = get_random_VA_videos_OMG(df_videos, n_videos=N_VIDEOS)#get_random_videos(df_videos, n_videos=N_VIDEOS)

        #START HEADER OF THE VIDEO ANSWERING PAGE (AND FORM):
        finalTemplate = create_header_videos(annotatorID, gender, englishLevel, studies,age,nationality,race, currentTimestamp)
        #START QUESTION/ANSWERS AND VIDEOS ATTACHEMENT
        # Load csv with questions to ask:
        df_questions = pd.read_csv("static/extraInfo/questions.csv", sep=";", header=0)
        #randomize questions except 1st and last questions and use the same order along the same form:
        df_questions = pd.concat(
            [df_questions[:1], df_questions[1:-3].sample(frac=1), pd.DataFrame(df_questions.tail(3))]).reset_index(
            drop=True)

        n=0
        for i, video_i in df_selected_videos.iterrows():
            finalTempl = template_videos_onfly(df_questions=df_questions,vid=video_i["vid"], start=str(int(video_i["start"])), end=str(math.ceil(video_i["end"])),vidName="Video"+str(n), videoID=video_i["video"])
            finalTemplate+=finalTempl
            n+=1
        #END FORM AND ADD SUBMIT BUTTON
        form_end = create_end_videos()
        finalTemplate += form_end
        return finalTemplate


def filter_answers(answer):
    return answer.split("(")[0].strip()


#Video Form
@app.route("/end", methods = ['POST'])
def finalForm():
    # Render HTML with count variable
    #GET USERS INFO ####################
    # Access to fields by its name
    annotatorID = request.form['annotatorID']
    gender = request.form['gender']
    englishLevel = request.form['englishLevel']
    studies = request.form['studies']
    age = request.form['age']
    nationality = request.form['nationality']
    race = request.form['race']
    currentTimestamp = request.form['timestamp']
    timeTaken = (int(time.time())-int(currentTimestamp))/60 #Seconds converted to min
    print(timeTaken)

    #GET VIDEOS INFO ##################
    df_questions = pd.read_csv("static/extraInfo/questions.csv", sep=";", header=0)
    dict_conversions = {"-3":-3, "-2":-2,"-1":-1,"0":0, "1":1,"2":2,"3":3, "Yes":True, "No":False}
    #TO DO -> EXTRA FILTER FOR ALL THE OPTIONS TO REMOVE PARENTHESIS OF ANSWERS

    if request.method == 'POST':
        ############# CREATE CONNECTION:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        #################################

        create_table(conn, table_name=TABLE_NAME)
        complete_list_answers = []
        for video_i in range(N_VIDEOS):
            video_id = request.form["Video"+str(video_i)]
            list_answers_video = [video_id]
            for i, row in df_questions.iterrows():
                if(row["TypeQuestion"]=="MultiOption"):
                    answerQuestion = ";".join(request.form.getlist(row["ID"]+"Video"+str(video_i)))
                else:
                    answerQuestion = request.form[row["ID"] + "Video" + str(video_i)]
                    if(row["ID"]!="Emotion"): #convert to the correct type
                        #answerQuestion = dict_conversions[answerQuestion]
                        answerQuestion = dict_conversions[filter_answers(answerQuestion)]

                list_answers_video.append(answerQuestion)
            #Add last textArea info:
            answerQuestion = request.form["TextArea" + "Video" +str(video_i)]
            list_answers_video.append(answerQuestion)


            complete_list_answers+=list_answers_video
        #SAVE ANSWERS:
        complete_list_answers = [annotatorID, gender, englishLevel, studies, int(age), nationality, race, timeTaken]+complete_list_answers
        insert_annotation(conn,values2insert=complete_list_answers,table_name=TABLE_NAME)
        conn.close()

    return render_template("final.html")




#Video Form
@app.route("/checkAnnotations", methods = ['GET','POST'])
def checkAnnotations():
    if request.method == 'GET':
        finalTemplate = get_checkAnnotations()

    elif request.method == 'POST':
        #Get data and repeat the same:
        videoID = request.form['id']
        actionvideo = request.form['action2do']
        df_videos = pd.read_csv("static/extraInfo/videos.csv", sep=",", header=0)
        if(actionvideo == "Recover"):
            df_videos_backup = pd.read_csv("static/extraInfo/videos_backup.csv", sep=",", header=0)
            video2recover = df_videos_backup.loc[df_videos_backup["video"] == videoID]
            df_videos = df_videos.append(pd.DataFrame(video2recover, columns=df_videos.columns))
        else: #Remove
            # Remove video from videos.csv
            df_videos = df_videos.loc[df_videos["video"] != videoID]

        #Save:
        df_videos.to_csv("static/extraInfo/videos.csv", sep=",", header=True, index=False)
        #Calculate prob matrix again:
        create_probability_table()
        finalTemplate = get_checkAnnotations()

    return finalTemplate


def get_checkAnnotations():
    # Get annotations:
    hed = create_header_HTML()
    ############# CREATE CONNECTION:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    #################################
    dict_annotations = count_annotations(conn, table_name=TABLE_NAME)
    dict_nationalities = check_nationalities(conn, table_name=TABLE_NAME)
    count_per_nationalities = count_annotations_per_nationalities(conn, dict_nationalities,table_name=TABLE_NAME)
    conn.close()
    # Check for differences between backup_videos and videos:
    df_videos_backup = pd.read_csv("static/extraInfo/videos_backup.csv", sep=",", header=0)
    df_videos = pd.read_csv("static/extraInfo/videos.csv", sep=",", header=0)
    videosOnlyInBackup = set(list(df_videos_backup["video"])).difference(set(list(df_videos["video"])))

    #HEADER TABLE
    html = '<table><tr>' \
           '<th> Form </th>' \
           '<th> VideoID </th>' \
           '<th> Counter </th>' \
           '<th> Remove/Recover Video </th>'


    for nationality in dict_nationalities:
        html += '<th> '+nationality[0]+' </th>'

    html+='</tr>'

    #BODY TABLE
    for key in list(dict_annotations.keys()):
        if (dict_annotations[key] >= MINANNOTATIONS):
            style2add = 'style="color:red;"'
        else:
            style2add = ''

        if(key in videosOnlyInBackup):
            tagButton = "Recover"
        else:
            tagButton = "Remove"

        html += '<tr>' \
                '<td><form id="formv'+str(key)+'" method="post" action="/checkAnnotations"><input type="hidden" name="id" value="'+str(key)+'" /><input type="hidden" name="action2do" value="'+str(tagButton)+'" /></form></td>' \
                '<td>' + str(key) + '</td>' \
                '<td ' + style2add + '>' + str(dict_annotations[key]) + '</td>' \
                '<td><input class="btn-block" form="formv' + str(key) + '" type="submit" id="v' + key + '" value="' + tagButton + '"></td>'

        if(key in count_per_nationalities.keys()):
            for nationality in dict_nationalities:
                 html +='<td>' + str(count_per_nationalities[key][nationality[0]]) + '</td>'
        else:
            for nationality in dict_nationalities:
                 html +='<td>' + str(0) + '</td>'

        html += '</tr>'
    #'<td><form action="/checkAnnotations" method="post"><input type="submit" class="btn-block" value="Remove"></form></td>' \
    finalTemplate = hed + html + """</table></div></body></html>"""
    return finalTemplate













if __name__ == "__main__":
    app.run()



