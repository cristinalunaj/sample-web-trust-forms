import os
## CONFIG VARS/FILES
DESCRIPTION = "Thank you very much for your cooperation!  <br>" \
                  "This is an anonymous survey that would take <strong>no more than 10 minutes</strong> to complete. " \
                  "We are a team of multinational researchers studying the effects of <strong>TRUST</strong> " \
                  "during a brief intervention at zero acquaintance. <br>" \
                  "It is important that you rate each person in the videos objectively - specifically, " \
                  "<strong>how</strong> the information is expressed (the behaviour/action), and not what is said (the content of the message). <br> Let's start!"
N_VIDEOS = 8
TABLE_NAME = "trustOMGTable"
DATABASE_URL = "dbname=suppliers user=cris" #os.environ['DATABASE_URL']  #"dbname=suppliers user=cris"  #"dbname=suppliers user=cris" #os.environ['DATABASE_URL']  #"dbname=suppliers user=cris" # # "dbname=suppliers user=cris"  # os.environ['DATABASE_URL']    ### local: "dbname=suppliers user=cris" ## heroku: os.environ['DATABASE_URL']
MINANNOTATIONS = 3