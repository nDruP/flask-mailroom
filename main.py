import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session
from peewee import fn
from model import Donation, Donor

app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('report'))


@app.route('/report/', methods=['GET'])
def report():
    return render_template('report.jinja2',
                           donor_info=donor_info(), donations=Donation.select())


@app.route('/add_donation', methods=['GET', 'POST'])
def add_donation():    
    if request.method == 'POST':
        donor_name = request.form['donor']
        amount = request.form['gift']
        try:
            donor = Donor.select().where(Donor.name == donor_name).get()
        except Donor.DoesNotExist:
            donor = Donor(name=donor_name)
            donor.save()
        Donation(donor=donor, value=amount).save()
        return redirect(url_for('thank_you', name=donor_name, amount=amount))

    return render_template('add_donation.jinja2', donors=Donor.select())


@app.route('/thank_you')
def thank_you():
    if request.method == 'POST':
        donor_name = request.form['donor']
        amount = request.form['gift']
        try:
            donor = Donor.select().where(Donor.name == donor_name).get()
        except Donor.DoesNotExist:
            donor = Donor(name=donor_name)
            donor.save()
        Donation(donor=donor, value=amount).save()
        return redirect(url_for('thank_you', name=donor_name, amount=amount))
    return render_template('thank_you.jinja2',
                           name=request.args.get('name'),
                           amount=request.args.get('amount'))


@app.route('/projection', methods=['GET', 'POST'])
def run_projection():
    if request.method == 'POST':
        maximum = request.form['max']
        minimum = request.form['min']
        factor = request.form['factor']
        return render_template('projection.jinja2',
                               info = donor_info(minimum, maximum, factor))
    return render_template('projection.jinja2')


def donor_info(minimum=0, maximum=99999999999999999, factor=1):
    info = (Donation
            .select(Donation.donor,
                    fn.COUNT(Donation.value).alias('num_gift'),
                    fn.SUM(factor*Donation.value).alias('sum_gift'),
                    fn.AVG(factor*Donation.value).alias('avg_gift'))
            .where(Donation.value >= minimum, Donation.value <= maximum)
            .group_by(Donation.donor)
            .order_by(Donation.donor))
    return info


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)

