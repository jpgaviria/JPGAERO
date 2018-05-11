import PyPDF2
import os, glob
import datetime
import xlsxwriter
#import textract

def main():
    ECMDB = ['']
    i = 1
    os.chdir('O:\\OEMPrograms1\\M-145\\CustomerCommunications\\RC-BA')
    #os.chdir('C:\\Users\jpgaviri\iCloudDrive\Personal\Python\ECM')
    for file in glob.glob("*.pdf"):
        print(file)
        #text = textract.process('file', method='pdfminer')
        #file = open('11229.pdf', 'rb')
        fileReader = PyPDF2.PdfFileReader(file)
        page = fileReader.getPage(0)
        text = page.extractText()
        for char in range(len(text)):
            if text[char] == 'S' and text[char:char+7]=='Subject':
                Start = char + 8
            elif text[char] == 'A' and text[char:char+9]=='Attention':
                End = char -1
        subject = text[Start:End]
        subject = subject.replace('\n',' ')
        ECMDB.append(['',''])
        ECMDB[i][0] = str(file)
        ECMDB[i][1] = str(subject)
        #ECMDB[i][1] = ECMDB[i][1].replace('Microsoft Word - ','')
        i+=1
    os.chdir('C:\\Users\jpgaviri\iCloudDrive\Personal\Python\ECM')
    now = datetime.datetime.now()
    ECMDBname = 'ECM_DB' + now.strftime("%Y-%m-%d-%H%M") +'.xlsx'
    wb = xlsxwriter.Workbook(ECMDBname)
    ws = wb.add_worksheet("ECM_DB")
    ws.set_column(0,0,20)
    ws.set_column(1,1,100)
    position_format = wb.add_format()
    position_format.set_border()
    position_format.set_text_wrap()
    position_format.set_align("left")
    position_format.set_align("top")
    for row in range(0,len(ECMDB)):
        for column in range(0,len(ECMDB[row])):
            ws.write(row,column,str(ECMDB[row][column]),position_format)
    print(ECMDB)

#----------------------------------------------------------------------
if __name__ == "__main__":
    main()