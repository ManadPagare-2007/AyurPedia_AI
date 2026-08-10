import json
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from supabase import create_client, Client

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")
supabase: Client = create_client(url, key) if url and key else None

def index(request):
    return render(request, 'home.html')

def query(request):
    return render(request, 'query.html')

def reviews(request):
    return render(request, 'review.html')

def feedback(request):
    return render(request, 'feedback.html')

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        if not supabase:
            return JsonResponse({'success': False, 'error': 'Database configuration is missing. Please set SUPABASE_URL and SUPABASE_KEY in Vercel environment variables.'}, status=500)
        try:
            data = json.loads(request.body)
            email = data.get('email') # Mapped to username
            password = data.get('password')
            role = data.get('role', 'User')

            role = 'Admin' if role.lower() == 'admin' else 'User'

            response = supabase.table('auth_user').select('username,password').eq('username', email).eq('password', password).execute()
            
            print(f"DEBUG email={repr(email)} password={repr(password)}")
            print(f"DEBUG response.data={response.data}")

            # Also do a username-only lookup to check if user exists at all
            check = supabase.table('auth_user').select('username,password').eq('username', email).execute()
            print(f"DEBUG user-only check={check.data}")

            if response.data:
                user_data = response.data[0]
                db_role = user_data.get('role')
                
                if role == 'Admin' and db_role != 'Admin':
                    return JsonResponse({'success': False, 'error': 'Account does not have admin privileges'}, status=403)
                
                return JsonResponse({'success': True, 'message': 'Login successful'})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_signup(request):
    if request.method == 'POST':
        if not supabase:
            return JsonResponse({'success': False, 'error': 'Database configuration is missing. Please set SUPABASE_URL and SUPABASE_KEY in Vercel environment variables.'}, status=500)
        try:
            data = json.loads(request.body)
            email = data.get('email') # Mapped to username
            password = data.get('password')
            role = data.get('role', 'User')
            
            role = 'Admin' if role.lower() == 'admin' else 'User'
            
            # Check if exists
            response = supabase.table('auth_user').select('username').eq('username', email).execute()
            if response.data:
                return JsonResponse({'success': False, 'error': 'Username/Email already in use'}, status=400)
            
            # Insert
            supabase.table('auth_user').insert({
                'username': email,
                'password': password,
                'role': role
            }).execute()
            
            return JsonResponse({'success': True, 'message': 'Account created'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_forgot(request):
    if request.method == 'POST':
        if not supabase:
            return JsonResponse({'success': False, 'error': 'Database configuration is missing. Please set SUPABASE_URL and SUPABASE_KEY in Vercel environment variables.'}, status=500)
        try:
            data = json.loads(request.body)
            email = data.get('email')
            new_password = data.get('password')
            
            response = supabase.table('auth_user').select('username').eq('username', email).execute()
            if not response.data:
                return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
            
            supabase.table('auth_user').update({'password': new_password}).eq('username', email).execute()
            return JsonResponse({'success': True, 'message': 'Password updated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)