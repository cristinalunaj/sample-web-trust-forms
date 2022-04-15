import psycopg2
import pandas as pd
from CONFIG import N_VIDEOS


def create_table(conn, table_name="trustTable"):
    cur = conn.cursor()
    df_questions = pd.read_csv("static/extraInfo/questions.csv", sep=";", header=0)
    type_question = ["bool", "smallint", "smallint","smallint","smallint","smallint","smallint","varchar","smallint","smallint","varchar"]
    command ="CREATE TABLE IF NOT EXISTS "+table_name+" (id serial PRIMARY KEY, gender varchar, studyLevel varchar, age smallint, nationality varchar, race varchar"

    for videoi in range(N_VIDEOS):
        command += ", IDv" + str(videoi) + " varchar"
        for i, rowQuestion in df_questions.iterrows():
            command+=", "+rowQuestion["ID"]+"v"+str(videoi) + " " +type_question[i]

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


def remove_values_table(conn, table_name="trusttabletest"):
    cur = conn.cursor()
    command = "DELETE FROM "+table_name
    cur.execute(command)
    conn.commit()
    cur.close()





def insert_annotation(conn, values2insert=[], table_name="trusttabletest"):
    cur = conn.cursor()
    df_questions = pd.read_csv("static/extraInfo/questions.csv", sep=";", header=0)
    command = "INSERT INTO "+table_name+" (gender, studylevel, age, nationality, race"

    for videoi in range(N_VIDEOS):
        command += ", IDv" + str(videoi)
        for i, rowQuestion in df_questions.iterrows():
            command+=", "+rowQuestion["ID"]+"v"+str(videoi)

    command += ") VALUES (%s, %s, %s, %s, %s" + "".join([", %s"]*N_VIDEOS*(len(df_questions)+1))+")"
    cur.execute(command, values2insert)
    conn.commit()
    cur.close()


