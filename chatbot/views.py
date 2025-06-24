from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import OTPVerification
from .forms import RegisterForm
import google.generativeai as genai
import random


def home(request):
    return render(request, "home.html")

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            # Generate OTP and send email
            otp = str(random.randint(100000, 999999))
            OTPVerification.objects.create(user=user, otp=otp)
            send_mail(
                "Your OTP Code",
                f"Your OTP is {otp}",
                "your_email@gmail.com",
                [user.email],
                fail_silently=False,
            )

            request.session["user_id"] = user.id  # Store user in session
            return redirect("otp_verify")  # ✅ Redirects to OTP page

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})

         



def otp_verify(request):
    user_id = request.session.get("user_id")
    
    if not user_id:
        return redirect("register")  # If session expires, go back to register
    
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        otp_obj = OTPVerification.objects.get(user=user)

        if otp_obj.otp == entered_otp:
            del request.session["user_id"]  # Remove user session after OTP verification
            return redirect("login")  # Redirect to login page instead of home
        else:
            return render(request, "otp_verify.html", {"error": "Invalid OTP"})

    return render(request, "otp_verify.html")






def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("chatbot")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")






genai.configure(api_key="enter your api key")


def chatbot(request):
    if "chat_history" not in request.session:
        request.session["chat_history"] = []  # Initialize chat history

    chat_history = request.session["chat_history"]  # Load previous messages
    bot_response = None

    if request.method == "POST":
        user_input = request.POST.get("message")

        prompt = f"""
        You are a chatbot designed to give short, helpful responses. 
        Keep answers under 50 words and provide home remedies if asked.

        User: {user_input}
        Assistant:
        """

        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)

        # Generate response with a word limit
        bot_response = " ".join(response.text.split()[:50]) if response and response.text else "I'm sorry, I couldn't generate a response."

        # Append new messages correctly
        chat_history.append({"sender": "user", "text": user_input})
        chat_history.append({"sender": "bot", "text": bot_response})

        request.session["chat_history"] = chat_history  # Update session
        request.session.modified = True  

    return render(request, "chat.html", {"chat_history": chat_history})
