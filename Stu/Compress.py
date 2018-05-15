import PyPDF2
import subprocess

path = 'C:\\Users\\jpgaviri\\iCloudDrive\\Personal\\Python\\Stu\\output.pdf'
path2 = 'C:\\Users\\jpgaviri\\iCloudDrive\\Personal\\Python\\Stu\\output2.pdf'
pdfs = [path, path2]

writer = PyPDF2.PdfFileWriter()

#for pdf in pdfs:
reader = PyPDF2.PdfFileReader(path2)
#subprocess.run(["qpdf", "--decrypt", "C:\\Users\\jpgaviri\\iCloudDrive\\Personal\\Python\\Stu\\Parts_3120720_01-31-18_ANSI_English.pdf",\
#                 "C:\\Users\\jpgaviri\\iCloudDrive\\Personal\\Python\\Stu\\output.pdf"])
for i in range(reader.numPages):
    page = reader.getPage(i)
    page.compressContentStreams()
    writer.addPage(page)

with open('test_out.pdf', 'wb') as f:
    writer.write(f)