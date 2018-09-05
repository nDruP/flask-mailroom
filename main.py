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
    return render_template('thank_you.jinja2',
                           name=request.args.get('name'),
                           amount=request.args.get('amount'))


def donor_info():
    info = (Donation
            .select(Donation.donor,
                    fn.COUNT(Donation.value).alias('num_gift'),
                    fn.SUM(Donation.value).alias('sum_gift'),
                    fn.AVG(Donation.value).alias('avg_gift'))
            .group_by(Donation.donor)
            .order_by(Donation.donor))
    return info


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)

