import os
## CONFIG VARS/FILES
DESCRIPTION = "Thank you very much for your cooperation!  " \
                  "This is an anonymous survey that would take <strong>no more than 10 minutes</strong> to complete. " \
                  "We are a team of multinational researchers studying the effects of <strong>TRUST</strong> " \
                  "during a brief intervention at zero acquaintance. " \
                  "It is important that you rate each person in the videos objectively - specifically, " \
                  "<strong>how</strong> the information is expressed (the behaviour/action), and not what is said (the content of the message). Let's start!"
N_VIDEOS = 2
TABLE_NAME = "trusOMGTable"
DATABASE_URL = os.environ['DATABASE_URL'] #os.environ['DATABASE_URL']  #"dbname=suppliers user=cris" # # "dbname=suppliers user=cris"  # os.environ['DATABASE_URL']    ### local: "dbname=suppliers user=cris" ## heroku: os.environ['DATABASE_URL']
