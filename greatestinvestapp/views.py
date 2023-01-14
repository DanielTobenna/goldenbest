from django.shortcuts import render, redirect, reverse

from django.core.mail import BadHeaderError, send_mail

from django.http import HttpResponse,HttpResponseRedirect

from django.contrib import messages

from django.contrib.auth import login, authenticate, logout

from django.contrib.auth.forms import UserCreationForm

from django.core.mail import EmailMessage

from django.conf import settings

from django.template.loader import render_to_string

from django.core.mail import EmailMultiAlternatives

from .models import *

from .forms import *

from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth.decorators import login_required

from django.utils.html import strip_tags

import datetime
import json
import requests
import uuid
import os

# Create your views here.

def home(request):
	return render(request, 'greatestinvestapp/index.html')


def plan(request):
	return render(request, 'greatestinvestapp/plan.html')

def otherpayment(request):
    return render(request, 'greatestinvestapp/otherpayment.html')


def about(request):
	return render(request, 'greatestinvestapp/company.html')


def career(request):
	return render(request, 'greatestinvestapp/career.html')


def signin(request):
	if request.user.is_authenticated:
		return redirect('dashboard')

	else:
		if request.method == "POST":
			username= request.POST.get('username')
			password= request.POST.get('password')

			user= authenticate(request, username=username, password=password)

			if user is not None:
				email= User.objects.get(username=username).email
				print(email)
				template= render_to_string('greatestinvestapp/loginAlert.html', {'name':username})
				plain_message= strip_tags(template)
				email_message= EmailMultiAlternatives(
					'Login alert on your account!',
					plain_message,
					settings.EMAIL_HOST_USER,
					[email]

					)
				email_message.attach_alternative(template, 'text/html')
				#email_message.send()
				login(request, user)
				return redirect('dashboard')

			else:
				messages.error(request, "username or password is incorrect")

	context={}
	return render(request, 'greatestinvestapp/login.html')


def privacy(request):
	return render(request, 'greatestinvestapp/privacy.html')

def main_view(request, *args, **kwargs):
	code= str(kwargs.get('ref_code'))

	try:
		client = Client.objects.get(code=code)
		request.session['ref_client'] = client.id
		print('id', client.id)
	except:
		pass
	print(request.session.get_expiry_age())

	return render(request, 'greatestinvestapp/main.html')


def signup(request):
	user_check = request.user.is_authenticated
	if user_check:
		return redirect('dashboard')
	client_id= request.session.get('ref_client')
	print('client_id', client_id)
	form = CreateUserForm(request.POST or None)
	if form.is_valid():
		if client_id is not None:
			recommended_by_client= Client.objects.get(id=client_id)
			recommended_by_client_email= recommended_by_client.email_address
			recommended_by_client_name= recommended_by_client.first_name
			username=form.cleaned_data.get('username')

			instance= form.save()
			registered_user= User.objects.get(id=instance.id)
			registered_client= Client.objects.get(user=registered_user)
			registered_client.recommended_by= recommended_by_client.user
			referral_template= render_to_string('greatestinvestapp/referalsignupmail.html', {'name':recommended_by_client_name, 'refereed':username})
			plain_message= strip_tags(referral_template)
			email_message= EmailMultiAlternatives(
				'You refered a user using your referral link',
				plain_message,
				settings.EMAIL_HOST_USER,
				[recommended_by_client_email],
				)
			email_message.attach_alternative(referral_template, 'text/html')
			#email_message.send()
			registered_client.save()

		else:
			form.save()

		username=form.cleaned_data.get('username')
		password= form.cleaned_data.get('password1')
		email= form.cleaned_data.get('email')
		template= render_to_string('greatestinvestapp/welcomeEmail.html', {'name':username})
		plain_message= strip_tags(template)
		email_message= EmailMultiAlternatives(
			'Welcome on board to Avalanche Invests!',
			plain_message,
			settings.EMAIL_HOST_USER,
			[email],

			)
		email_message.attach_alternative(template, 'text/html')
		#email_message.send()
		#try:
			#send_mail(username, "A client with username: {} has just signed up on your site with email: {}".format(username, email),email, ['support@avalancheinvests.co.uk'])
		#except BadHeaderError:
			#return HttpResponse("Your account has been created but you can't login at this time. please, try to login later")
		user= authenticate(username=username, password=password)
		login(request, user)
		return redirect('dashboard')
	context={'form':form}
	return render(request, 'greatestinvestapp/register.html', context)

@login_required(login_url='signin')
def dashboard(request):
	if request.user.is_staff:
		return redirect('admindashboard')
	else:
		client= request.user.client
		client_firstname= request.user.username
		client_email= request.user.email
		client_pk= client.pk
		client_deposit= client.deposit
		client_profit= client.profit
		client_bal= client.balance
		client_withdrawal= client.withdrawal
		client_date_joined= client.created
		client_code= client.code
		client.save()
	context={'client': client, 'client_deposit':client_deposit, 'client_bal':client_bal,'client_profit':client_profit, 'client_date_joined':client_date_joined,
	'client_withdrawal':client_withdrawal, 'client_code':client_code }
	return render(request, 'greatestinvestapp/dashboard.html', context)

@login_required(login_url='signin')
@staff_member_required
def admindashboard(request):
	clients= Client.objects.all()
	withdrawal_requests= Withdrawal_request.objects.all()
	transactions= Transaction.objects.all()
	clients_total= clients.count()
	withdrawal_requests_total= withdrawal_requests.count()
	transactions_total= transactions.count()
	payment= Payment_id.objects.all()
	context={'clients_total':clients_total, 'withdrawal_requests_total':withdrawal_requests_total, 'transactions_total':transactions_total,
	"clients":clients, 'payment':payment  }
	return render(request, 'greatestinvestapp/adminpage.html', context)


def terms(request):
	return render(request, 'greatestinvestapp/terms.html')


def realestate(request):
	return render(request, 'greatestinvestapp/realestate.html')


def crypto(request):
	return render(request, 'greatestinvestapp/crypto.html')


def forex(request):
	return render(request, 'greatestinvestapp/forex.html')


def nft(request):
	return render(request, 'greatestinvestapp/nft.html')


def contact(request):
	return render(request, 'greatestinvestapp/contact.html')


def stocks(request):
	return render(request, 'greatestinvestapp/stocks.html')


def agriculture(request):
	return render(request, 'greatestinvestapp/agriculture.html')


def gold(request):
	return render(request, 'greatestinvestapp/gold.html')


def retirement(request):
	return render(request, 'greatestinvestapp/retirement.html')

@login_required(login_url='signin')
def deposit(request):
	if request.method=='POST':
		client= request.user.client
		client_name= client.first_name
		client_email= client.email_address
		#post data to create invoice for payment
		price_amount= request.POST.get('price_amount')
		price_currency= "usd"
		pay_currency= request.POST.get('pay_currency')
		order_id= 'Quantum Finance'
		order_description= "This is a plan subscription"
		if price_amount and pay_currency:
			# Api's url link
			url= 'https://api.nowpayments.io/v1/invoice'
			payload=json.dumps({
				"price_amount": price_amount,
				"price_currency": price_currency,
				"pay_currency": pay_currency,
				"order_id": order_id,
				"order_description": order_description,
				"ipn_callback_url": "https://nowpayments.io",
				"success_url": "https://www.quantumfinancecompany.com/dashboard",
				#our success url will direct us to the get_payment_status view for balance top ups
				"cancel_url": "https://www.quantumfinancecompany.com/dashboard"
			})
			headers={'x-api-key':'XKEXE2R-Q5447YK-N7Q6V63-EC0JXKY', 'Content-Type': 'application/json'}
			response= requests.request('POST', url, headers=headers, data=payload)
			res= response.json()
			print(res)
			generated_link= res["invoice_url"]
			generated_payment_id= res["id"]
			#Now get the user and add the payment ID to the database as we will be using it to know their payment status
			Payment_id.objects.create(
				client=client,
				payment_id= generated_payment_id,
				price_amount= price_amount,
				)
			try:
				send_mail(client_name, "A client with username: {} has created a deposit request with an amount ${}".format(client_name, price_amount),client_email, ['support@avalancheinvests.co.uk'])
			except BadHeaderError:
				pass
			return redirect(generated_link)
	context={}
	return render(request, 'greatestinvestapp/deposit.html', context)

@login_required(login_url='signin')
def withdrawal(request):
	client= request.user.client
	client_id= client.id
	client_username= request.user.username
	client_email= client.email_address
	client_deposit= client.deposit
	client_withdrawal= client.withdrawal
	minimum_withdrawal= Minimum_withdrawal.objects.all()
	maximum_withdrawal= Maximum_withdrawal.objects.all()
	for i in minimum_withdrawal:
		minimum_withdrawal_amount= i.minimum_withdrawal
	for i in maximum_withdrawal:
		maximum_withdrawal_amount= i.maximum_withdrawal
	print(client_deposit)
	client_profit= client.profit
	client_balance= client.balance
	client_info= Client.objects.filter(id=client_id)
	if request.method =='POST':
		withdrawal_option = request.POST.get('withdrawal_category')
		amount= request.POST.get('amount')
		withdrawal_address= request.POST.get('withdrawal_address')
		crypto= request.POST.get('crypto')
		if withdrawal_option == 'balance' and float(client_balance) > float(minimum_withdrawal_amount):
			client_current_balance= float(client_balance) - float(amount)
			client_withdrawal_balance= float(client_withdrawal) + float(amount)
			if float(client_current_balance) < 0 or float(client_balance) > float(maximum_withdrawal_amount):
				messages.error(request, "The amount requested is greater than your balance or you are exceeding the maximum withdrawal amount")
			else:
				client_update= client_info.update(balance=client_current_balance, withdrawal=client_withdrawal_balance)
				Withdrawal_request.objects.create(
					client= client,
					client_username= client_username,
					client_email= client_email,
					crypto_used_for_requesting_withdrawal= crypto,
					withdrawal_address= withdrawal_address,
					amount= amount
					)
				try:
					send_mail(client_username, "A client with username: {} has requested a withdrawal of {}".format(client_username, amount),client_email, ['support@avalancheinvests.co.uk'])

				except BadHeaderError:
					return HttpResponse('Something went wrong, please try again later')

				return HttpResponse('Withdrawal submitted successfully')


		if withdrawal_option == 'balance' and float(client_balance)<= float(minimum_withdrawal_amount):
			messages.error(request, "Your balance is too low for this withdrawal or your request is less than the minimum withdrawal amount")

		if withdrawal_option == 'profit' and float(client_profit) > 10:
			client_profit_balance= float(client_profit) - float(amount)
			client_withdrawal_balance= float(client_withdrawal) + float(amount)
			if client_profit_balance < 0:
				messages.error(request, "Amount requested is greater than profit")
			else:
				client_update= client_info.update(profit= client_profit_balance, withdrawal=client_withdrawal_balance)
				Withdrawal_request.objects.create(
					client= client,
					client_username= client_username,
					client_email= client_email,
					crypto_used_for_requesting_withdrawal= crypto,
					withdrawal_address= withdrawal_address,
					amount= amount
					)
				try:
					send_mail(client_username, "A client with username: {} has requested a withdrawal of {}".format(client_username, amount),client_email, ['support@avalancheinvests.co.uk'])
				except BadHeaderError:
					return HttpResponse('Something went wrong, please try again later')

		if withdrawal_option == 'profit' and float(client_profit) <=10:
			messages.error(request, "Your profit is too low for this withdrawal" )
	context={}
	return render(request, 'greatestinvestapp/withdrawal.html', context)

@login_required(login_url='signin')
def history(request):
	client= request.user.client
	transaction= ''
	try:
		transaction= Transaction.objects.filter(client=client)
		total_transaction= transaction.count()
	except:
		pass
	context={'transaction':transaction, 'total_transaction':total_transaction }
	return render(request, 'greatestinvestapp/history.html', context)

@login_required(login_url='signin')
def myreferals(request):
    info= request.user
    client= Client.objects.get(user=info)
    ref_info= client.get_recommended_profiles()
    client_code= client.code
    context={'ref_info': ref_info, 'client_code':client_code}
    return render(request, 'greatestinvestapp/referralprofiles.html', context)

@login_required(login_url='signin')
@staff_member_required
def confirm_withdrawal(request):
	withdrawalInfo= Withdrawal_request.objects.all()
	context={'withdrawalInfo': withdrawalInfo}
	return render(request, 'greatestinvestapp/confirmwithdrawal.html', context)

@login_required(login_url='signin')
@staff_member_required
def update_withdrawal(request, pk):
	withdrawalInfo= Withdrawal_request.objects.get(id=pk)
	withdrawalInfo_id= withdrawalInfo.id
	withdrawalInfo_amount= withdrawalInfo.amount
	withdrawal_address= withdrawalInfo.withdrawal_address
	client_id= withdrawalInfo.client.id
	client= Client.objects.get(id=client_id)
	client_bal= client.deposit
	client_name= client.first_name
	client_email= client.email_address
	client_withdrawal= client.withdrawal
	template= render_to_string('greatestinvestapp/withdrawalEmail.html', {'name': client_name, 'amount':withdrawalInfo_amount, 'wallet_address':withdrawal_address})
	plain_message= strip_tags(template)
	emailmessage= EmailMultiAlternatives(
		'Congratulations, Your withdrawal request has been approved!',
		plain_message,
		settings.EMAIL_HOST_USER,
		[client_email],
		)
	emailmessage.attach_alternative(template, 'text/html')
	emailmessage.send()
	delete_withdrawal= withdrawalInfo.delete()
	return HttpResponse('Update withdrawal')

@login_required(login_url='signin')
@staff_member_required
def decline_wihdrawal(request, pk):
	withdrawalInfo= Withdrawal_request.objects.get(id=pk)
	withdrawalInfo_id= withdrawalInfo.id
	withdrawalInfo_amount= withdrawalInfo.amount
	withdrawal_address= withdrawalInfo.withdrawal_address
	client_id= withdrawalInfo.client.id
	client= Client.objects.get(id=client_id)
	client_info= Client.objects.filter(id=client_id)
	client_bal= client.balance
	client_name= client.first_name
	client_email= client.email_address
	client_withdrawal= client.withdrawal
	client_balance_reup= float(client_bal) + float(withdrawalInfo_amount)
	client_withdrawal_reup= float(client_withdrawal) - float(withdrawalInfo_amount)
	client_info_update= client_info.update(balance=client_balance_reup, withdrawal=client_withdrawal_reup)
	template= render_to_string('greatestinvestapp/declineWithdrawalEmail.html', {'name': client_name, 'amount':withdrawalInfo_amount, 'wallet_address':withdrawal_address})
	plain_message= strip_tags(template)
	emailmessage= EmailMultiAlternatives(
		'Withdrawal request declined!',
		plain_message,
		settings.EMAIL_HOST_USER,
		[client_email],
		)
	emailmessage.attach_alternative(template, 'text/html')
	emailmessage.send()
	Transaction.objects.create(
		client=client,
		transaction_type='Withdrawal',
		amount= withdrawalInfo_amount,
		status= 'Declined'
		)
	delete_withdrawal= withdrawalInfo.delete()
	return HttpResponse('Withdrawal request declined')


@login_required(login_url='signin')
@staff_member_required
def confirm_deposit(request):
	paymentInfo= Payment_id.objects.all()
	context={'paymentInfo': paymentInfo}
	return render(request, 'greatestinvestapp/confirmdeposit.html', context)


@login_required(login_url='signin')
@staff_member_required
def update_payment(request, pk):
	payment_info= Payment_id.objects.get(id=pk)
	payment_info_id= payment_info.id
	payment_info_amount= payment_info.price_amount
	client_id= payment_info.client.id
	client= Client.objects.get(id=client_id)
	client_deposit= client.deposit
	client_pk= client.id
	client_name= client.first_name
	client_email= client.email_address
	print(client_deposit)
	client_info= Client.objects.filter(id=client_pk)
	newClientbal= float(payment_info_amount) + float(client_deposit)
	update_payment= client_info.update(deposit=newClientbal, running_days=0)
	template= render_to_string('greatestinvestapp/confirmDepositEmail.html', {'name':client_name, 'amount':payment_info_amount})
	plain_message= strip_tags(template)
	emailmessage= EmailMultiAlternatives(
		'Congratulations, Your deposit was successful!',
		plain_message,
		settings.EMAIL_HOST_USER,
		[client_email],

		)
	emailmessage.attach_alternative(template, 'text/html')
	emailmessage.send()

	Transaction.objects.create(
		client=client,
		transaction_type='Deposit',
		amount= payment_info_amount,
		status= 'Approved'
		)
	delete_payment_info= payment_info.delete()
	if update_payment:
		return HttpResponse('deposit confirmed successfully')
	return HttpResponse('Update payment')

@login_required(login_url='signin')
def account_settings(request):

	client= request.user.client

	form=ClientForm(instance=client)

	if request.method=='POST':
		form= ClientForm(request.POST, request.FILES, instance=client)
		if form.is_valid():
			form.save()

	context= {"form":form}
	return render(request, 'greatestinvestapp/account_settings.html', context)

@login_required(login_url='signin')
def create_bonus(request):
	if request.method == 'POST':
		client_username= request.POST.get('client_username')
		amount= request.POST.get('amount')
		code= request.POST.get('code')
		if client_username and amount and code:
			user_check= User.objects.get(username=client_username)
			if user_check :
				client_id= user_check.client.id
				client_email= user_check.email
				if client_email and client_id:
					bonus_code= Bonus.objects.get(code=code)
					if bonus_code:
						return HttpResponse('sorry this code already exists, please create some other code')
					else:
						Bonus.objects.create(
							client=client_id,
							email= client_email,
							transaction_type= 'Bonus Reward',
							amount= amount,
							code= code,
						)
						template= render_to_string('greatestinvestapp/bonusNotification.html', {'name':user_check.username, 'amount':amount, 'code':code})
						plain_message= strip_tags(template)
						emailmessage= EmailMultiAlternatives(
							'Congratulations, You have recieved a bonus reward!',
							plain_message,
							settings.EMAIL_HOST_USER,
							[client_email],
							)
						emailmessage.attach_alternative(template, 'text/html')
						#emailmessage.send()
						try:
							pass
						except BadHeaderError:
							pass
				else:
					return HttpResponse('Client details is not complete, please update details.')
			else:
				return HttpResponse('Client details is not complete, please update details.')

	context={}
	return render(request, 'greatestinvestapp/create_bonus.html', context)

@login_required(login_url='signin')
def use_bonus(request):
	client= request.user.client
	context={}
	return render(request, 'greatestinvestapp/use_bonus.html', context)


def logoutuser(request):
	logout(request)
	return redirect('signin')


	
	