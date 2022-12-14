## sample-web-trust-forms

    * static
        |_bkgn_images: Folder with the background image for the web page (not important...)
        |_extraInfo
            |_ question.csv: Csv with the question to include per form and their possible answers. Headers:
                    *TypeQuestion: Whether the question allow single option or several options (multi-option)
                    *ID: ID to identify the question when coding and to access it easily
                    *Text: Actual question/text that the user will see. <strong></strong> marks indicate that the part inside should be in bold.
                    *Options: Answer options that the user has to choose, each option is divided by a comma (',').Example:[-3 (Extremely NOT attractive),-2 (Very NOT...]
            |_videos.csv: Csv with the information of the OMG dataset and the videos employed in annotations. For understanding the headers, check the README of OMG.
                    But the most important is the 'link' which is the youtube link to the video (Important: some of them are down or they do not exist anymore...).
            |_videos_backup.csv: Same (or similar) file to videos.csv. The reason of having a copy is because videos.csv was prepared to be modified (removing or adding videos) when necessary
                    according to the number of annotations collected per video. On the opposite, the backup version was expected to be non-mutable to recover videos removed from 'videos.csv' if required.
            |_videosProbMatrix.pkl: Matrix with the probability of displaying a video according to the number of annotations of this video.
            |_stylesheets: Folders with the format of the web pages (color, style and so on)
        |_templates: Folders with the code of the htmls view. Start in: 1)index.html, 2)personalData; 3) (The is generated on the fly)); 4)final.html
                ->check_video_annotations.html is an additional web for cehcking number of annotations (for us, not for users)
    *app.py: It is the main controller/router of the web page. Any GET/POST request is received in this application and processed.
         The first route is '/', the rest of routes would be called internally automatically after user click on 'Next'.
         The route '/checkAnnotations' could be also used to check the number of annotations, videos annotated per nationality and remove/add videos to the set of videos to annotate.
    *helpers_back.py: Functions to work with the database (add/delete rows, create table...). (*Probably we will need to adapt this file to the new platform and database)
    *helpers_front.py: Functions to render html pages and which control the order in which videos are selected and displayed in the forms.
        The most important goal of these functions is to randomize order in whcih videos are displayed (inside the form and between forms,
        e.g. mixing some videos from fomr1 with some of form2 for creating form3, randomizing the order of each set
        AND also to randomize the order in which questions are displayed (except for question of Visibility that should always appear in position 1
        and Trust and ReasonTrust that should appear in this order at the end)
            e.g. Form1: Visibility, Expressiveness, Kindness, Authenticity, ..., Trust, ReasonTrust
                 Form2: Visibility, Authenticity, Kindness, Expressiveness, ..., Trust, ReasonTrust
                 ...
    *CONFIG.py: Contain some variables to modify some parameters of the platform such as the initial description,
        the number of videos per form, the name of the database, the URL, and the minimum number of annotations per video for
        being removed from the list.

