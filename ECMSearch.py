import PyPDF2
import os, glob
import datetime
import xlsxwriter
#import textract

def main():
    ECMDB = []
    ECMDB.append(['','','',''])
    ECMDB[0][0] = 'ECM Number'
    ECMDB[0][1] = 'ECM Date'
    ECMDB[0][2] = 'ECM Subject'
    ECMDB[0][3] = 'ECM Attachments'    
    i = 1
    #os.chdir('O:\\OEMPrograms1\\M-145\\CustomerCommunications\\RC-BA')
    os.chdir('C:\\Users\\jpgaviri\\Documents\\RCI\\Mdrive_copy\\Customercommunication\\RC-BA')
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
        for char in range(len(text)):
            if text[char] == 'D' and text[char:char+5]=='Date:':
                Start = char + 5
            elif text[char] == 'P' and text[char:char+6]=='Pages:':
                End = char -1
        date = text[Start:End]
        date = date.replace('\n',' ')

        found = False
        for char in range(len(text)):
            if text[char] == 'A' and text[char:char+15]=='Attachments 4.1':
                Start = char + 12
                found = True
            elif text[char] == 'A' and text[char:char+16]=='Attachments\n 4.1':
                Start = char + 13
                found = True
            elif text[char] == 'N' and text[char:char+8]=='Notice -':
                End = char -1
        Attachment = 'N/A'
        if found:
            Attachment = text[Start:]
            Attachment = Attachment.replace('\n',' ')
            for char in range(len(Attachment)):
                if Attachment[char] == ' ' and Attachment[char:char+3]==' 4.':
                    Attachment = list(Attachment)
                    Attachment[char] = "\n"
                    Attachment = ''.join(Attachment)        
        else:
            Attachment = 'N/A'
        ECMDB.append(['','','',''])
        name = str(file)
        name = name.replace('.pdf','')
        ECMDB[i][0] = name
        ECMDB[i][1] = str(date)
        ECMDB[i][2] = str(subject)
        ECMDB[i][3] = str(Attachment)
        #ECMDB[i][1] = ECMDB[i][1].replace('Microsoft Word - ','')
        i+=1
    os.chdir('C:\\Users\\jpgaviri\\iCloudDrive\\Personal\\Python\\ECM')
    now = datetime.datetime.now()
    ECMDBname = 'ECM_DB' + now.strftime("%Y-%m-%d-%H%M") +'.xlsx'
    wb = xlsxwriter.Workbook(ECMDBname)
    ws = wb.add_worksheet("ECM_DB")
    ws.set_column(0,0,20)
    ws.set_column(1,1,20)
    ws.set_column(2,2,80)
    ws.set_column(3,4,80)
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