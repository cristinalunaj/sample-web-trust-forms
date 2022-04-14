from flask import Flask, render_template, request
import pandas as pd
import math
from CONFIG import *
from helpers_front import *
from helpers_back import *

########## DATABASE CONNECTIONS
import os
import psycopg2

DATABASE_URL = os.environ[
    'DATABASE_URL']  # "dbname=suppliers user=cris"  # os.environ['DATABASE_URL']    ### local: "dbname=suppliers user=cris" ## heroku: os.environ['DATABASE_URL']
# Connect to database
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

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
        gender = request.form['genderQ']
        studies = request.form['StudyQ']
        age = request.form['AgeQ']
        nationality = request.form['nationalityQ']
        race = request.form['RaceQ']


        #Get videos web:
        df_videos = pd.read_csv("static/extraInfo/videos.csv", sep=",", header=0)
        df_selected_videos = get_random_videos(df_videos, n_videos=N_VIDEOS)

        #START HEADER OF THE VIDEO ANSWERING PAGE (AND FORM):
        finalTemplate = create_header_videos(gender, studies,age,nationality,race)
        #START QUESTION/ANSWERS AND VIDEOS ATTACHEMENT
        n=0
        for i, video_i in df_selected_videos.iterrows():
            finalTempl = template_videos_onfly(vid=video_i["vid"], start=str(int(video_i["start"])), end=str(math.ceil(video_i["end"])),vidName="video"+str(n), videoID=video_i["video"])
            finalTemplate+=finalTempl
            n+=1
        #END FORM AND ADD SUBMIT BUTTON
        form_end = """<input type="submit" value="Submit"></form>"""
        finalTemplate += form_end
        return finalTemplate


#Video Form
@app.route("/end", methods = ['POST'])
def finalForm():
    # Render HTML with count variable
    #GET USERS INFO ####################
    # Access to fields by its name
    gender = request.form['gender']
    studies = request.form['studies']
    age = request.form['age']
    nationality = request.form['nationality']
    race = request.form['race']

    #GET VIDEOS INFO ##################
    df_questions = pd.read_csv("static/extraInfo/questions.csv", sep=";", header=0)
    dict_conversions = {"-3 (Nothing)":-3, "-2":-2,"-1":-1,"0":0, "1":1,"2":2,"3 (A lot)":3, "Yes":True, "No":False}
    if request.method == 'POST':
        create_table(conn, table_name=TABLE_NAME)
        complete_list_answers = []
        for video_i in range(N_VIDEOS):
            video_id = request.form["video"+str(video_i)]
            list_answers_video = [video_id]
            for i, row in df_questions.iterrows():
                if(row["TypeQuestion"]=="MultiOption"):
                    answerQuestion = ";".join(request.form.getlist(row["ID"]+"video"+str(video_i)))
                else:
                    answerQuestion = request.form[row["ID"] + "video" + str(video_i)]
                    if(row["ID"]!="Emotion"): #convert to the correct type
                        answerQuestion = dict_conversions[answerQuestion]

                list_answers_video.append(answerQuestion)
            complete_list_answers+=list_answers_video
        #SAVE ANSWERS:
        complete_list_answers = [gender, studies, int(age), nationality, race]+complete_list_answers
        insert_annotation(conn,values2insert=complete_list_answers,table_name=TABLE_NAME)





    return render_template("final.html")

if __name__ == "__main__":

    app.run()
    conn.close()


