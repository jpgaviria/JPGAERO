#import xlsxwriter
#import xlrd
import datetime
from openpyxl import Workbook
from openpyxl import load_workbook
from jira import JIRA
import numpy as np
import os
import time
#import csv 

Expenses_File = "expenses.xlsx"
Transactions_File = "transactions_June_08_2018.xlsx"
os.chdir('C:\\Users\\jpgaviri\\iCloudDrive\\Personal\\Python\\Expenses')
def Update_Expenses(Expenses, Transactions):

    

    TransactionsWS = Transactions['transactions_June_08_2018']
    
    NumRows = TransactionsWS.max_row
    # NumColumn = TransactionsWS.max_column
    ForeignX = 1

    for transaction in range(2,NumRows):
        date = TransactionsWS.cell(transaction, 1).value.strftime('%d_%m_%Y')
        #print (date)
        # Generate tabs for every month in the expenses file
        match = False
        SheetNames = Expenses.sheetnames
        for sheet in SheetNames:
            if date[3:] == sheet:
                match = True
                break
        if match == False:
            Expenses.create_sheet(date[3:])
            ActiveSheet = Expenses[date[3:]]
            ActiveSheet.cell(1,1).value = date[3:]
            ActiveSheet.cell(1,2).value = "USD Exchange rate"
            ActiveSheet.cell(1,3).value = 1.30
            ActiveSheet.cell(2,1).value = "Date"
            ActiveSheet.cell(2,2).value = "Description"
            ActiveSheet.cell(2,3).value = "milleage @ .55 per km"
            ActiveSheet.cell(2,4).value = "$ total milleage"
            ActiveSheet.cell(2,5).value = "meal description"
            ActiveSheet.cell(2,6).value = "meal cost"
            ActiveSheet.cell(2,7).value = "Utilities"
            ActiveSheet.cell(2,8).value = "Travel"
            ActiveSheet.cell(2,9).value = "health"
            ActiveSheet.cell(2,10).value = "parking"
            ActiveSheet.cell(2,11).value = "clothing"
            ActiveSheet.cell(2,12).value = "tickets"
            ActiveSheet.cell(2,13).value = "Rent"
            ActiveSheet.cell(2,15).value = "Other - Category"
            ActiveSheet.cell(2,16).value = "$ Amount"
            dateraw = TransactionsWS.cell(transaction, 1).value
            LastRow = ActiveSheet.max_row + 1
            DayOfMonth = dateraw.replace(day=1)
            for day in range(1,31):
                # Charge the rent + parking
                if DayOfMonth.day ==1:
                    ActiveSheet.cell(LastRow,1).value = DayOfMonth 
                    ActiveSheet.cell(LastRow,2).value = "Office Rent"   
                    ActiveSheet.cell(LastRow,13).value = 1133   
                    LastRow +=1
                # on weekdays add the per diem for gas                    
                if DayOfMonth.weekday() != 5 and DayOfMonth.weekday() != 6:
                    ActiveSheet.cell(LastRow,1).value = DayOfMonth
                    ActiveSheet.cell(LastRow,2).value = "Work at Customer site"   
                    ActiveSheet.cell(LastRow,3).value = 64   
                    ActiveSheet.cell(LastRow,4).value = 35.2
                    LastRow +=1 
                DayOfMonth = DayOfMonth + datetime.timedelta(days=+1)
                if DayOfMonth.day ==1:
                    break
            month = dateraw.month

        # Add each transaction to the correct month
        ActiveSheet = Expenses[date[3:]]
        LastRow = ActiveSheet.max_row
        # Hide transfer transactions as they don't provide much value
        if (TransactionsWS.cell(transaction, 6).value != "Transfer"):
            ActiveSheet.cell(LastRow +1,1).value = TransactionsWS.cell(transaction, 1).value 
            ActiveSheet.cell(LastRow +1,2).value = TransactionsWS.cell(transaction, 2).value
        # if the cost is in a USD card then multiply by the exchange
        if (TransactionsWS.cell(transaction, 7).value == "Starwood Preferred Guest") or \
                (TransactionsWS.cell(transaction, 7).value == "CREDIT CARD") or \
                (TransactionsWS.cell(transaction, 7).value == "Bank of America Cash Rewards Visa Platinum Plus ") or \
                (TransactionsWS.cell(transaction, 7).value == "Green Card"):
            ForeignX =  ActiveSheet.cell(1,3).value
        else :
            ForeignX = 1
        # add the cost to each category or to the other at the end
        if (TransactionsWS.cell(transaction, 6).value == "Restaurants") or \
                (TransactionsWS.cell(transaction, 6).value == "Coffee Shops") or \
                (TransactionsWS.cell(transaction, 6).value == "Fast Food") or \
                (TransactionsWS.cell(transaction, 6).value == "Food & Dining"):
            ActiveSheet.cell(LastRow +1,6).value = (TransactionsWS.cell(transaction, 4).value * ForeignX)
        elif (TransactionsWS.cell(transaction, 6).value == "Mobile Phone") or \
                (TransactionsWS.cell(transaction, 6).value == "Internet") or \
                (TransactionsWS.cell(transaction, 6).value == "Utilities"):
            ActiveSheet.cell(LastRow +1,7).value = (TransactionsWS.cell(transaction, 4).value * ForeignX)
        elif (TransactionsWS.cell(transaction, 6).value == "Parking"):
            ActiveSheet.cell(LastRow +1,10).value = (TransactionsWS.cell(transaction, 4).value * ForeignX)
        elif (TransactionsWS.cell(transaction, 6).value == "Health & Fitness") or \
                (TransactionsWS.cell(transaction, 6).value == "Gym") or \
                (TransactionsWS.cell(transaction, 6).value == "Doctor"):
            ActiveSheet.cell(LastRow +1,9).value = (TransactionsWS.cell(transaction, 4).value * ForeignX)
        elif (TransactionsWS.cell(transaction, 6).value == "Rental Car & Taxi") or \
                (TransactionsWS.cell(transaction, 6).value == "Travel") or \
                (TransactionsWS.cell(transaction, 6).value == "Air Travel"):
            ActiveSheet.cell(LastRow +1,8).value = (TransactionsWS.cell(transaction, 4).value * ForeignX)
        elif (TransactionsWS.cell(transaction, 6).value == "Clothing"):
            ActiveSheet.cell(LastRow +1,11).value = (TransactionsWS.cell(transaction, 4).value * ForeignX)
        elif (TransactionsWS.cell(transaction, 6).value == "Transfer"):
            continue
        else :
            ActiveSheet.cell(LastRow +1,16).value = (TransactionsWS.cell(transaction, 4).value * ForeignX)
            ActiveSheet.cell(LastRow +1,15).value = TransactionsWS.cell(transaction, 6).value

    # add the column totals and then the grand total
    SheetNames = Expenses.sheetnames
    for sheet in SheetNames:
        ActiveSheet = Expenses[sheet]
        LastRow = ActiveSheet.max_row
        RowTotal = 0
        for row in range(3,LastRow):
            RowTotal += float(ActiveSheet.cell(row,4).value)     
        ActiveSheet.cell(LastRow +2,4).value = RowTotal
        RowTotal = 0
        for row in range(3,LastRow):
            RowTotal += float(ActiveSheet.cell(row,5).value)     
        ActiveSheet.cell(LastRow +2,5).value = RowTotal
        RowTotal = 0
        for row in range(3,LastRow):
            RowTotal += float(ActiveSheet.cell(row,6).value)    
        ActiveSheet.cell(LastRow +2,6).value = RowTotal
        RowTotal = 0
        for row in range(3,LastRow):
            RowTotal += float(ActiveSheet.cell(row,7).value )    
        ActiveSheet.cell(LastRow +2,7).value = RowTotal
        RowTotal = 0
        for row in range(3,LastRow):
            RowTotal += float(ActiveSheet.cell(row,8).value )    
        ActiveSheet.cell(LastRow +2,8).value = RowTotal
        RowTotal = 0
        for row in range(3,LastRow):
            RowTotal += float(ActiveSheet.cell(row,9).value )    
        ActiveSheet.cell(LastRow +2,9).value = RowTotal
        RowTotal = 0
        for row in range(3,LastRow):
            RowTotal += float(ActiveSheet.cell(row,10).value  )   
        ActiveSheet.cell(LastRow +2,10).value = RowTotal
        RowTotal = 0
        for row in range(3,LastRow):
            RowTotal += float(ActiveSheet.cell(row,11).value )    
        ActiveSheet.cell(LastRow +2,11).value = RowTotal
        RowTotal = 0
        for row in range(3,LastRow):
            RowTotal += float(ActiveSheet.cell(row,12).value )    
        ActiveSheet.cell(LastRow +2,12).value = RowTotal
        RowTotal = 0
        for row in range(3,LastRow):
            RowTotal += float(ActiveSheet.cell(row,13).value  )   
        ActiveSheet.cell(LastRow +2,13).value = RowTotal

    # CRs = ['' for x in range(NumRows+1)]
    # newTotalData = VDD.copy_worksheet(TotalDataWS)
    # newTotalData.title = 'New TD jira'
    # AllM145Issues = VDD.create_sheet('AllM145')
    # #for row in range(1,NumRows):
    # for row in range(1,NumRows+1):
    #     CRs[row] = str(TotalDataWS[row][8].value)
    # # cleanup list of CRs so that only 1 CR per
    # for row in range(1,len(CRs)):
    #     i=0
    #     for char in CRs[row]:
    #         if char == '\n':
    #             CRs[row] = CRs[row][:i]
    #         elif char == 'O' and CRs[row][i:i+3] == 'OMS' and i>3:
    #             CRs[row] = CRs[row][:i]
    #         elif char == 'I' and CRs[row][i:i+4] == 'IFIS' and i>3:
    #             CRs[row] = CRs[row][:i]
    #         elif char == 'E' and CRs[row][i:i+5] == 'EICAS' and i>3:
    #             CRs[row] = CRs[row][:i]
    #         elif char == 'F' and CRs[row][i:i+4] == 'FDSA' and i>3:
    #             CRs[row] = CRs[row][:i]
    #         i+=1
    # options = {'server': 'http://alm.rockwellcollins.com/issues/'}
    # jira = JIRA(options, basic_auth=('jpgaviri','PSWD*'))#Use RCI password
    # # Get all projects viewable by anonymous users.
    # projects = jira.projects()
    # M145 = jira.project('GLOBALA')
    # #M145_issues = jira.search_issues('project=GLOBALA')
    # block_size = 100
    # block_num = 0
    # i = 1
    # while True:
    #     start_idx = block_num*block_size
    #     M145_issues = jira.search_issues('project=GLOBALA', start_idx, block_size)
    #     #---------------------

    #     Wp_type, summary, description, function, fix_version, affected_projects,labels, \
    #         Operational_impact,Plain_English,Criticality = '','','','','','','','','',''
    #     for issue in M145_issues:
    #         print (issue)
    #         Wp_type, summary, description, function, fix_version, affected_projects,labels, \
    #             Operational_impact,Plain_English,Criticality = '','','','','','','','','',''
    #         #english_description = issue.raw['fields']['customfield_20330']
    #         for field in issue.raw['fields']:
    #             if field == 'customfield_12909':
    #                 if issue.raw['fields']['customfield_12909'] != None:
    #                     Wp_type = issue.raw['fields']['customfield_12909']['value']
    #             if field == 'summary':
    #                 if issue.raw['fields']['summary'] != None:
    #                     summary = issue.raw['fields']['summary']
    #             if field == 'description':
    #                 if issue.raw['fields']['description'] != None:
    #                     description = issue.raw['fields']['description']
    #             if field == 'customfield_19307':
    #                 if issue.raw['fields']['customfield_19307'] != None:
    #                     function = issue.raw['fields']['customfield_19307']['value']
    #             if field == 'fixVersions':
    #                 if issue.raw['fields']['fixVersions'] != []:
    #                     fix_version = issue.raw['fields']['fixVersions'][0]['name']
    #             if field == 'customfield_13705':
    #                 if issue.raw['fields']['customfield_13705'] != None:
    #                     affected_projects = issue.raw['fields']['customfield_13705']
    #             if field == 'labels':
    #                 if issue.raw['fields']['labels'] != None:
    #                     labels = issue.raw['fields']['labels']
    #             if field == 'customfield_12906':
    #                 if issue.raw['fields']['customfield_12906'] != None:
    #                     Operational_impact = issue.raw['fields']['customfield_12906']
    #             if field == 'customfield_18527':
    #                 if issue.raw['fields']['customfield_18527'] != None:
    #                     Plain_English = issue.raw['fields']['customfield_18527']
    #             if field == 'customfield_13514':
    #                 if issue.raw['fields']['customfield_13514'] != []:
    #                     Criticality = issue.raw['fields']['customfield_13514'][0]
    #         #last_update = issue.raw['fields']['customfield_19063']
    #         print ("this seems to have worked")
    #         label = ''
    #         if labels != '':
    #             for l in labels: 
    #                 label = label + ', ' + str(l)
    #         label = str(label)

    #         AllM145Issues[i][0].value = 'CR NUmber: ' + str(issue.key) + '\n' \
    #                                     'Work Package Type: ' + str(Wp_type) + '\n' \
    #                                     + 'Fix Version: '+ str(fix_version) +'\n' \
    #                                     + 'Labels: '+ str(label) + '\n' \
    #                                     + 'Summary: ' + str(summary) + '\n' \
    #                                     + 'Operational Impact: '+ str(Operational_impact) +'\n' \
    #                                     + 'English Description: '+ str(Plain_English) +'\n' \
    #                                     + 'Description: ' + str(description) +'\n'
    #         #AllM145Issues[i][1].value = issue.key
    #         i+=1
        
    #     #--------------------
    #     time.sleep(5) 
    #     if len(M145_issues) == 0:
    #         # Retrieve issues until there are no more to come
    #         break
    #     block_num += 1


    # i = 1
    # Wp_type, summary, description, function, fix_version, affected_projects,labels, \
    #     Operational_impact,Plain_English,Criticality = '','','','','','','','','',''
    # for issue in M145_issues:
    #     print (issue)
    #     Wp_type, summary, description, function, fix_version, affected_projects,labels, \
    #         Operational_impact,Plain_English,Criticality = '','','','','','','','','',''
    #     #english_description = issue.raw['fields']['customfield_20330']
    #     for field in issue.raw['fields']:
    #         if field == 'customfield_12909':
    #             if issue.raw['fields']['customfield_12909'] != None:
    #                 Wp_type = issue.raw['fields']['customfield_12909']['value']
    #         if field == 'summary':
    #             if issue.raw['fields']['summary'] != None:
    #                 summary = issue.raw['fields']['summary']
    #         if field == 'description':
    #             if issue.raw['fields']['description'] != None:
    #                 description = issue.raw['fields']['description']
    #         if field == 'customfield_19307':
    #             if issue.raw['fields']['customfield_19307'] != None:
    #                 function = issue.raw['fields']['customfield_19307']['value']
    #         if field == 'fixVersions':
    #             if issue.raw['fields']['fixVersions'] != []:
    #                 fix_version = issue.raw['fields']['fixVersions'][0]['name']
    #         if field == 'customfield_13705':
    #             if issue.raw['fields']['customfield_13705'] != None:
    #                 affected_projects = issue.raw['fields']['customfield_13705']
    #         if field == 'labels':
    #             if issue.raw['fields']['labels'] != None:
    #                 labels = issue.raw['fields']['labels']
    #         if field == 'customfield_12906':
    #             if issue.raw['fields']['customfield_12906'] != None:
    #                 Operational_impact = issue.raw['fields']['customfield_12906']
    #         if field == 'customfield_18527':
    #             if issue.raw['fields']['customfield_18527'] != None:
    #                 Plain_English = issue.raw['fields']['customfield_18527']
    #         if field == 'customfield_13514':
    #             if issue.raw['fields']['customfield_13514'] != []:
    #                 Criticality = issue.raw['fields']['customfield_13514'][0]
    #     #last_update = issue.raw['fields']['customfield_19063']
    #     print ("this seems to have worked")
    #     label = ''
    #     if labels != '':
    #         for l in labels: 
    #             label = label + ', ' + str(l)
    #     label = str(label)

    #     AllM145Issues[i][0].value = 'Work Package Type: ' + str(Wp_type) + '\n' \
    #                                 + 'Fix Version: '+ str(fix_version) +'\n' \
    #                                 + 'Labels: '+ str(label) + '\n' \
    #                                 + 'Summary: ' + str(summary) + '\n' \
    #                                 + 'Operational Impact: '+ str(Operational_impact) +'\n' \
    #                                 + 'English Description: '+ str(Plain_English) +'\n' \
    #                                 + 'Description: ' + str(description) +'\n'
    #     AllM145Issues[i][1].value = str(issue)
    #     i+=1

    # i=1
    # for CR in CRs:
    #     if CR != '' and CR != 'CRID' and CR != 'GLOBALA-XXXX' and CR != 'Globala-XXX' and CR != 'GLOBALA-TBD':
    #         if CR[:6] == 'GLOBAL':
    #             issue = jira.issue(str(CR))
    #             print (CR)
    #             function, Operational_impact, Plain_English = '','',''
    #             #english_description = issue.raw['fields']['customfield_20330']
    #             if issue.raw['fields']['customfield_12909'] != None:
    #                 Wp_type = issue.raw['fields']['customfield_12909']['value']
    #             if issue.raw['fields']['summary'] != None:
    #                 summary = issue.raw['fields']['summary']
    #             if issue.raw['fields']['description'] != None:
    #                 description = issue.raw['fields']['description']
    #             if issue.raw['fields']['customfield_19307'] != None:
    #                 function = issue.raw['fields']['customfield_19307']['value']
    #             if issue.raw['fields']['fixVersions'] != None:
    #                 fix_version = issue.raw['fields']['fixVersions'][0]['name']
    #             if issue.raw['fields']['customfield_13705'] != None:
    #                 affected_projects = issue.raw['fields']['customfield_13705']
    #             if issue.raw['fields']['labels'] != None:
    #                 labels = issue.raw['fields']['labels']
    #             if issue.raw['fields']['customfield_12906'] != None:
    #                 Operational_impact = issue.raw['fields']['customfield_12906']
    #             if issue.raw['fields']['customfield_18527'] != None:
    #                 Plain_English = issue.raw['fields']['customfield_18527']
    #             if issue.raw['fields']['customfield_13514'] != None:
    #                 Criticality = issue.raw['fields']['customfield_13514'][0]
    #             #last_update = issue.raw['fields']['customfield_19063']
    #             print ("this seems to have worked")
    #             label = ''
    #             for l in labels: 
    #                 label = label + ', ' + str(l)
    #             label = str(label)

    #             newTotalData[i][0].value = 'Work Package Type: ' + Wp_type + '\n' \
    #                                         + 'Fix Version: '+ fix_version +'\n' \
    #                                         + 'Labels: '+ label \
    #                                         + 'Summary: ' + summary + '\n' \
    #                                         + 'Operational Impact: '+ Operational_impact +'\n' \
    #                                         + 'English Description: '+ Plain_English +'\n' \
    #                                         + 'Description: ' + description +'\n'
    #     i+=1
    #print issue.fields.project.key
    #print issue.fields.issuetype.name
    #print issue.fields.reporter.displayName
    #print issue.fields.summary
    #print issue.fields.project.id
    return Expenses

def ReadFiles():
    wb_Expenses = load_workbook(filename = Expenses_File)
    wb_Transactions = load_workbook(filename = Transactions_File)


    return wb_Expenses, wb_Transactions

if __name__== "__main__" :
     Expenses, Transactions = ReadFiles()
     Expenses = Update_Expenses(Expenses, Transactions)
     Expenses.save('UpdatedExpenses.xlsx')
