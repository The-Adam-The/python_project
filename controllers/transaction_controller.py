from urllib.request import Request
from flask import Flask, render_template, request, redirect
from flask import Blueprint
import datetime

from models.transaction import Transaction
from models.date import Date
from models.objects import filter 


import repositories.transaction_repository as transaction_repository
import repositories.tag_repository as tag_repository
import repositories.merchant_repository as merchant_repository

transaction_blueprint = Blueprint("transaction", __name__)

trans_last_output= []

#Create 
@transaction_blueprint.route('/transactions/new')
def new_transaction():
    tags = tag_repository.select_all()
    merchants = merchant_repository.select_all()
    return render_template('transactions/new.html', tags=tags, merchants=merchants)

@transaction_blueprint.route('/transactions', methods=['POST'])
def add_transaction():    
    date = request.form['date']
    amount = request.form['amount']
    merchant_id = request.form['merchant']
    tag_id = request.form['tag']

    merchant = merchant_repository.select(merchant_id)
    tag = tag_repository.select(tag_id)

    transaction = Transaction(date, amount, merchant, tag)
    transaction_repository.save(transaction)
    return redirect('/transactions')

#transaction main
@transaction_blueprint.route('/transactions')
def transactions():

    all_transactions = transaction_repository.select_all()
    all_tags = tag_repository.select_all()
    all_merchants = merchant_repository.select_all()

    global filter

    if filter.merchant_id:
        if filter.tag_id:
            filtered_transactions = transaction_repository.select_by_date_merchant_tag(filter.start_date, filter.end_date, filter.merchant_id, filter.tag_id)
        else:
            filtered_transactions = transaction_repository.select_by_date_merchant(filter.start_date, filter.end_date, filter.merchant_id)
    else:
        if filter.tag_id:
            filtered_transactions = transaction_repository.select_by_date_tag(filter.start_date, filter.end_date, filter.tag_id)
        else:
            filtered_transactions = transaction_repository.select_by_date(filter.start_date, filter.end_date)

    
    total_spent = Transaction.total_spending(filtered_transactions) 

    for transaction in filtered_transactions:
        transaction = transaction.amount_formatted()

    return render_template('transactions/index.html', filtered_transactions=filtered_transactions, total_spent=total_spent, filter=filter, all_tags=all_tags, all_merchants=all_merchants)


@transaction_blueprint.route('/transactions/change_date', methods=['POST'])
def change_date_transactions():
    global filter

    filter.start_date = request.form['start_date']
    filter.end_date = request.form['end_date']
    
    if request.form['merchant'] == "":
        filter.merchant_id = None;

    else:
        filter.merchant_id = request.form['merchant']
    
    if request.form['tag'] == "":
        filter.tag_id = None
    else:
        filter.tag_id = request.form['tag']

    return redirect('/transactions')



@transaction_blueprint.route('/transactions/<id>')
def show(id):
    
    transaction = transaction_repository.select(id)
    daily_transactions = transaction_repository.select_by_date(transaction.date, transaction.date)
    total_spent = Transaction.total_spending(daily_transactions)
    
    return render_template('transactions/show.html', transaction=transaction, daily_transactions=daily_transactions, total_spent=total_spent)

#Update
@transaction_blueprint.route('/transactions/<id>/edit')
def edit_transaction(id):
    transaction = transaction_repository.select(id)
    tags = tag_repository.select_all()
    merchants = merchant_repository.select_all()
    return render_template('transactions/edit.html', transaction=transaction, merchants=merchants, tags=tags)


@transaction_blueprint.route('/transactions/<id>', methods=['POST'])
def update_transaction(id):
    date = request.form['date']
    amount = request.form['amount']
    merchant_id = request.form['merchant']
    tag_id = request.form['tag']

    trans_last_output = [date, amount, merchant_id, tag_id, id]

    merchant = merchant_repository.select(merchant_id)
    tag = tag_repository.select(tag_id)

    transaction = Transaction(date, amount, merchant, tag, id)
    transaction_repository.update_transaction(transaction)
    return redirect('/transactions')


#Delete
@transaction_blueprint.route('/transactions/<id>/delete', methods=['POST'])
def delete_transaction(id):
    transaction_repository.delete(id)
    return redirect('/transactions')
