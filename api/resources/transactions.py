from flask import Blueprint, jsonify, request
from peewee import DoesNotExist
from playhouse.shortcuts import model_to_dict
import datetime

from transaction import Transaction

transaction = Blueprint('transaction', __name__, url_prefix='/api/transaction')

@transaction.route('/add', methods=['POST'])
def add_transaction():
    body = request.get_json()
    transaction_add = Transaction.create(**body)
    transaction_dict = model_to_dict(transaction_add)
    return jsonify(transaction_dict), 201

@transaction.route('/spend/<int:pts>', methods=['GET'])
def spend_points(pts):
    try:
        all_transactions = [model_to_dict(transaction) for transaction in Transaction.select()]
        sorted_transactions = sorted(all_transactions, key=lambda a: a['timestamp'])
        point_vals = list(set([key['points'] for key in all_transactions]))
        total_pts = sum(point_vals)
        points_to_spend = pts
        payer_records = []
        if points_to_spend <= total_pts:
            for record in sorted_transactions:
                if points_to_spend <= 0:
                    break
                elif points_to_spend < record['points']:
                    updated_points = record['points'] - points_to_spend
                    payer_records = update_payer_records(payer_records, record, updated_points)
                    break
                elif points_to_spend == record['points']:
                    payer_records = update_payer_records(payer_records, record, points_to_spend)
                    break
                elif points_to_spend > record['points'] and record ['points'] > 0:
                    payer_records = update_payer_records(payer_records, record, record['points'])
                    points_to_spend -= record['points']
        return jsonify(payer_records)
    except DoesNotExist:
        return jsonify(message='Error, spend request'), 500

def update_payer_records(payer_records, record, points_to_add):
    payer = record['payer']
    points = record['points']
    if not payer_records:
        if points_to_add - points == 0:
            payer_records.append({'payer': payer, 'points': -points})
        else:
            payer_records.append({'payer': payer, 'points': points_to_add - points})
    else:
        updated = False
        for record in payer_records:
            if record['points'] < 0:
                continue
            if record['payer'] == payer:
                points = record['points']
                record.update({'points': points - points_to_add})
                updated = True
                break
        if not updated:
            if points > points_to_add:
                updated_pts = points - points_to_add
                payer_records.append({'payer': payer, 'points': -updated_pts})
            else:
                payer_records.append({'payer': payer, 'points': -points_to_add})
    if points_to_add - points == 0:
        new_transaction = {'payer': payer, 'points': -points, 'timestamp': datetime.datetime.now()}
        transaction_add = Transaction.create(**new_transaction)
        model_to_dict(transaction_add)
    elif points_to_add - points > 0:
        new_transaction = {'payer': payer, 'points': points, 'timestamp': datetime.datetime.now()}
        transaction_add = Transaction.create(**new_transaction)
        model_to_dict(transaction_add)
    else:
        new_transaction = {'payer': payer, 'points': points_to_add - points, 'timestamp': datetime.datetime.now()}
        transaction_add = Transaction.create(**new_transaction)
        model_to_dict(transaction_add)
    return payer_records

@transaction.route('/payer_balance', methods=['GET'])
def get_payer_balances():
    all_transactions = [model_to_dict(transaction) for transaction in Transaction.select()]
    payers = list(set([key['payer'] for key in all_transactions]))
    balance = {}
    for payer in payers:
        balance[payer] = 0
        for record in all_transactions:
            if record['payer'] == payer:
                balance[payer] += record['points']
    return jsonify(balance)


# These are some additional routes that I added to aid in debugging
@transaction.route('/')
def get_all_transactions():
    try:
        all_transactions = [model_to_dict(transaction) for transaction in Transaction.select()]
        sorted_transactions = sorted(all_transactions, key=lambda a: a['timestamp'])
        return jsonify(sorted_transactions)
    except DoesNotExist:
        return jsonify(message='Error getting transactions'), 500

@transaction.route('/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    try:
        (Transaction
            .delete()
            .where(Transaction.id == id)
            .execute())
        return jsonify(message='Transaction successfully removed'), 200
    except DoesNotExist:
        return jsonify(message='error deleting transaction'), 500

@transaction.route('/<int:id>', methods=['GET'])
def get_one_transaction(id):
    try:
        single_transaction = Transaction.get_by_id(id)
        return jsonify(model_to_dict(single_transaction)), 200
    except DoesNotExist:
        return jsonify(message='Error getting transaction'), 500
