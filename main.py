import pandas as pd
import numpy as np
import pdf2image
import requests
import PyPDF2
from io import BytesIO
import pdf2image
import cv2
import re
from io import BytesIO
import os
from urllib.parse import urlparse
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

#setting the csv data frames
source_xl = pd.read_csv('DATA/source.csv') #the urls for the questiion and answers pdfs
result_xl = pd.read_csv('DATA/result.csv') #the file with all the questions by subject with right answers
control_xl = pd.read_csv('DATA/control.csv') #a control file, used to check if there are mismatches between Q&A amount


for index,row in source_xl.iterrows():
    questions_url = row['Questions_URL']
    answers_url = row['Answers_URL']
    subject = row['Subject']
    type = row['Type']
    name = os.path.basename(urlparse(questions_url).path)[:-7]+'Q'
    save_dir = 'DATA/'+subject+'/'+type+'/'

    #getting the questions pdf and converting it to an image
    questions_response = requests.get(questions_url, timeout=30)
    images = pdf2image.convert_from_bytes(questions_response.content)
    images[0].save('DATA/temp.jpg', 'JPEG')
    page = cv2.imread('DATA/temp.jpg')

    image = page.copy()

    #OpenCV image proccessing to detect lines
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines_list = []
    lines = cv2.HoughLinesP(
        edges,  # Input edge image
        15,  # Distance resolution in pixels
        np.pi / 180,  # Angle resolution in radians
        threshold=100,  # Min number of votes for valid line
        minLineLength=1200,  # Min allowed length of line
        maxLineGap=10  # Max allowed gap between line for joining them
    )

    # drawing lines
    for points in lines:
        x1, y1, x2, y2 = points[0]
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        lines_list.append([(x1, y1), (x2, y2)])

    # saving each question (between to lines)
    amount_of_questions = len(lines_list) - 1
    lines_list.sort(key=lambda y: y[0][1])
    for i in range(amount_of_questions):
        x1, y1 = lines_list[i][0]
        x2, y2 = lines_list[i + 1][1]
        final_dir = save_dir + name + str(i + 2) + '.png'
        cv2.imwrite(final_dir, image[y1 + 2:y2 - 1, x1 - 10:x2-36])
        result_xl = result_xl.append({"Question": name + str(i + 2),"Question_Dir":final_dir,"Answer":"-"},ignore_index = True)

    #proccessing the answers
    answers_response = requests.get(answers_url, timeout=30)
    pdfFileObject = BytesIO(answers_response.content)
    # pdfFileObject = open('DATA/pace3sol.pdf', 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObject)
    first_page = pdfReader.getPage(0)
    text = first_page.extractText()
    amount_of_answers = 0
    #find all the answers (obviously there are less than 100, stop when can't find answer)
    for i in range(2,100):
        #using regex to detect the template of the answer, such as: "2 . ( 4 )"
        answer = x = re.findall(str(i)+"\s[.]\s[(]\s[1-4]", text)
        if len(answer) == 0:
            break
        else:
            #linking the answer to the right quesiton
            result_xl.loc[result_xl['Question'] == name + str(i), 'Answer'] = answer[0][-1]
            amount_of_answers += 1
    #adding to the control file (is checked manually later)
    control_xl = control_xl.append({"Questions_URL": questions_url, "Subject": subject, "Type": type,
                                  "AmountQ": amount_of_questions, "AmountA": amount_of_answers},
                                 ignore_index=True)
    print(name+","+type)
result_xl.to_csv("DATA/result.csv", index = False)
control_xl.to_csv("DATA/control.csv", index = False)
