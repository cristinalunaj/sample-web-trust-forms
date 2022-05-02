from flask import Flask, render_template, request
import pandas as pd
import math
from CONFIG import *
from helpers_front import *
from helpers_back import *

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
        studies = request.form['StudyQ']
        age = request.form['AgeQ']
        nationality = request.form['nationalityQ']
        race = request.form['RaceQ']


        #Get videos web:
        df_videos = pd.read_csv("static/extraInfo/videos.csv", sep=",", header=0)
        df_selected_videos = get_random_VA_videos_OMG(df_videos, n_videos=N_VIDEOS)#get_random_videos(df_videos, n_videos=N_VIDEOS)

        #START HEADER OF THE VIDEO ANSWERING PAGE (AND FORM):
        finalTemplate = create_header_videos(annotatorID, gender, studies,age,nationality,race)
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
    studies = request.form['studies']
    age = request.form['age']
    nationality = request.form['nationality']
    race = request.form['race']

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
        complete_list_answers = [annotatorID, gender, studies, int(age), nationality, race]+complete_list_answers
        insert_annotation(conn,values2insert=complete_list_answers,table_name=TABLE_NAME)
        conn.close()

    return render_template("final.html")

if __name__ == "__main__":
    app.run()



