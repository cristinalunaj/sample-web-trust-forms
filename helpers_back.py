import psycopg2
import pandas as pd
from CONFIG import N_VIDEOS


def create_table(conn, table_name="trustTable"):
    cur = conn.cursor()
    df_questions = pd.read_csv("static/extraInfo/questions.csv", sep=";", header=0)
    type_question = ["bool", "smallint", "smallint","smallint","smallint","smallint","smallint","varchar","smallint","smallint","varchar"]
    command ="CREATE TABLE IF NOT EXISTS "+table_name+" (id serial PRIMARY KEY, AnnotatorID varchar, gender varchar, englishLevel varchar, studyLevel varchar, age smallint, nationality varchar, race varchar, timeTaken smallint"

    for videoi in range(N_VIDEOS):
        command += ", IDv" + str(videoi) + " varchar"
        for i, rowQuestion in df_questions.iterrows():
            command+=", "+rowQuestion["ID"]+"v"+str(videoi) + " " +type_question[i]
        #Text are for others (multi-option) -> reason:
        command += ", otherTextAreav" + str(videoi) + " varchar"

    end_command = command+");"
    print(end_command)
    cur.execute(end_command)
    conn.commit()
    cur.close()





def export_table_data(conn, csvpath, table_name="trustTable"):
    cur = conn.cursor()
    command = "COPY "+table_name+" TO STDOUT  WITH DELIMITER ',' CSV HEADER;"
    with open(csvpath, "w") as file:
        cur.copy_expert(command, file)
    cur.close()


def remove_values_table(conn, table_name="trusttable"):
    cur = conn.cursor()
    command = "DELETE FROM "+table_name
    cur.execute(command)
    conn.commit()
    cur.close()





def insert_annotation(conn, values2insert=[], table_name="trusttable"):
    cur = conn.cursor()
    df_questions = pd.read_csv("static/extraInfo/questions.csv", sep=";", header=0)
    command = "INSERT INTO "+table_name+" (annotatorID, gender, englishLevel, studylevel, age, nationality, race, timeTaken"

    for videoi in range(N_VIDEOS):
        command += ", IDv" + str(videoi)
        for i, rowQuestion in df_questions.iterrows():
            command+=", "+rowQuestion["ID"]+"v"+str(videoi)
        command += ", otherTextAreav" + str(videoi)
    command += ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s" + "".join([", %s"]*N_VIDEOS*(len(df_questions)+2))+")"
    cur.execute(command, values2insert)
    conn.commit()
    cur.close()




def count_annotations(conn, table_name="trusttable"):
    cur = conn.cursor()
    df_videosComplete = pd.read_csv("static/extraInfo/videos_backup.csv", sep=",", header=0)
    dict_videos = dict.fromkeys(df_videosComplete["video"], 0)

    for i in range(N_VIDEOS):
        command = "SELECT IDv"+str(i)+", count(*) FROM "+table_name+" GROUP BY IDv"+str(i)+";"
        cur.execute(command)
        mobile_records = cur.fetchall()
        for row in mobile_records:
            dict_videos[row[0]]+=row[1]

    conn.commit()
    cur.close()
    return dict_videos



