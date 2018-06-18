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
Transactions_File = "transactions_june12_2018.xlsx"
os.chdir('C:\\Users\\jpgaviri\\iCloudDrive\\Personal\\Python\\Expenses')
def Update_Expenses(Expenses, Transactions):

    

    TransactionsWS = Transactions['transactions_june12_2018']
    
    NumRows = TransactionsWS.max_row
    # NumColumn = TransactionsWS.max_column
    # Read FX from Expenses
    ActiveSheet = Expenses['FX']
    Lastrow = ActiveSheet.max_row
    ForeignX = []
    for month in range(2,Lastrow+1):
        ForeignX.append([ActiveSheet.cell(month,1).value,ActiveSheet.cell(month,2).value])

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
            FX = 1.3
            for months in ForeignX:
                if date[3:] == months[0]:
                    FX = months[1]
            Expenses.create_sheet(date[3:])
            ActiveSheet = Expenses[date[3:]]
            ActiveSheet.cell(1,1).value = date[3:]
            ActiveSheet.cell(1,2).value = "USD Exchange rate"
            ActiveSheet.cell(1,3).value = FX
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
            for _ in range(1,31):
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
            MonthFX =  float(ActiveSheet.cell(1,3).value)
        else :
            MonthFX = 1
        # add the cost to each category or to the other at the end
        if (TransactionsWS.cell(transaction, 6).value == "Restaurants") or \
                (TransactionsWS.cell(transaction, 6).value == "Coffee Shops") or \
                (TransactionsWS.cell(transaction, 6).value == "Fast Food") or \
                (TransactionsWS.cell(transaction, 6).value == "Food & Dining"):
            Cost = float(TransactionsWS.cell(transaction, 4).value * MonthFX)
            ActiveSheet.cell(LastRow +1,6).value = Cost
        elif (TransactionsWS.cell(transaction, 6).value == "Mobile Phone") or \
                (TransactionsWS.cell(transaction, 6).value == "Internet") or \
                (TransactionsWS.cell(transaction, 6).value == "Office Supplies") or \
                (TransactionsWS.cell(transaction, 6).value == "Business Services") or \
                (TransactionsWS.cell(transaction, 6).value == "Shipping") or \
                (TransactionsWS.cell(transaction, 6).value == "Utilities"):
            Cost = float(TransactionsWS.cell(transaction, 4).value * MonthFX)
            ActiveSheet.cell(LastRow +1,7).value = Cost
        elif (TransactionsWS.cell(transaction, 6).value == "Parking"):
            Cost = float(TransactionsWS.cell(transaction, 4).value * MonthFX)
            ActiveSheet.cell(LastRow +1,10).value =Cost
        elif (TransactionsWS.cell(transaction, 6).value == "Health & Fitness") or \
                (TransactionsWS.cell(transaction, 6).value == "Gym") or \
                (TransactionsWS.cell(transaction, 6).value == "Doctor"):
            Cost = float(TransactionsWS.cell(transaction, 4).value * MonthFX)
            ActiveSheet.cell(LastRow +1,9).value = Cost
        elif (TransactionsWS.cell(transaction, 6).value == "Rental Car & Taxi") or \
                (TransactionsWS.cell(transaction, 6).value == "Travel") or \
                (TransactionsWS.cell(transaction, 6).value == "Hotel") or \
                (TransactionsWS.cell(transaction, 6).value == "Air Travel"):
            Cost = float(TransactionsWS.cell(transaction, 4).value * MonthFX)
            ActiveSheet.cell(LastRow +1,8).value = Cost
        elif (TransactionsWS.cell(transaction, 6).value == "Clothing"):
            Cost = float(TransactionsWS.cell(transaction, 4).value * MonthFX)
            ActiveSheet.cell(LastRow +1,11).value =Cost
        elif (TransactionsWS.cell(transaction, 6).value == "Transfer"):
            continue
        else :
            Cost = float(TransactionsWS.cell(transaction, 4).value * MonthFX)
            ActiveSheet.cell(LastRow +1,16).value = Cost
            ActiveSheet.cell(LastRow +1,15).value = TransactionsWS.cell(transaction, 6).value

    # add the column totals and then the grand total
    SheetNames = Expenses.sheetnames
    for sheet in SheetNames:
        ActiveSheet = Expenses[sheet]
        LastRow = ActiveSheet.max_row
        LastCol = ActiveSheet.max_column
        for j in range(4,LastCol+1):
            if j == 15:
                continue
            else:
                RowTotal = 0
                for i in range(3,LastRow):
                    if ActiveSheet.cell(i,j).value == None:
                        continue
                    else:
                        RowTotal += ActiveSheet.cell(i,j).value     
                ActiveSheet.cell(LastRow +2,j).value = RowTotal
        ActiveSheet.cell(LastRow +2,2).value = "Subtotals"
        ActiveSheet.cell(LastRow +4,12).value = "Total Expenses"
        GrandTotal = 0
        for j in range(4,14):
            if ActiveSheet.cell(LastRow +2,j).value == None:
                continue
            else:
                GrandTotal += ActiveSheet.cell(LastRow +2,j).value         
        ActiveSheet.cell(LastRow +4,14).value = float(GrandTotal) 
    return Expenses

def ReadFiles():
    wb_Expenses = load_workbook(filename = Expenses_File)
    wb_Transactions = load_workbook(filename = Transactions_File)


    return wb_Expenses, wb_Transactions

if __name__== "__main__" :
     Expenses, Transactions = ReadFiles()
     Expenses = Update_Expenses(Expenses, Transactions)
     Expenses.save('UpdatedExpenses.xlsx')
