import os
import base64

from flask import Flask, render_template, request, redirect, url_for
from peewee import fn
from model import Donation, Donor

app = Flask(__name__)
app.secret_key = base64.b32encode(os.urandom(16)).decode().strip('=')
# os.environ.get('SECRET_KEY').encode()


@app.route('/')
def home():
    return redirect(url_for('report'))


@app.route('/report/', methods=['GET'])
def report():
    return render_template('report.jinja2',
                           donor_info=donor_info(),
                           donations=Donation.select())


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


@app.route('/lifetime_thanks', methods=['GET', 'POST'])
def lifetime_thanks():
    if request.method == 'POST':
        donor_name = request.form['donor']
        try:
            donor = Donor.select().where(Donor.name == donor_name).get()
        except Donor.DoesNotExist:
            return render_template('lifetime.jinja2',
                                   error=donor_name+" Does Not Exist!")
        donor_sum = (
            Donation.select(fn.SUM(Donation.value).alias('total'))
            .where(Donation.donor == donor)
        )
        for d in donor_sum:
            amount = d.total
        return render_template('lifetime.jinja2',
                               name=donor_name, amount=amount)
    return render_template('lifetime.jinja2')


@app.route('/projection', methods=['GET', 'POST'])
def run_projection():
    if request.method == 'POST':
        maximum = request.form['max']
        minimum = request.form['min']
        factor = request.form['factor']
        return render_template('projection.jinja2',
                               info=donor_info(minimum, maximum, factor))
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
