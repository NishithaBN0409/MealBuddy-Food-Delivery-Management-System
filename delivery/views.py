import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Item # Assuming your cart logic tracks Items or a Cart mapping model
from .models import *

# Terminal Verification Box
print("\n" + "="*40)
print("SUCCESS: FINAL VERIFIED CODE IS ACTIVE")
print("="*40 + "\n")

# --- AUTH & NAVIGATION ---

def index(request): 
    # This shows the landing page with 'Sign In' and 'Create Account' buttons
    return render(request, 'index.html')

def open_signin(request): 
    return render(request, 'signin.html')

def open_signup(request): 
    return render(request, 'signup.html')

def signup(request): 
    # This handles the form submission from signup.html
    # For now, it redirects to the login page
    return redirect('open_signin')

def signin(request): 
    # This handles the form submission from signin.html
    # After login, the user should go to the restaurant list
    return redirect('open_show_restaurant')

def user_logout(request):
    request.session.flush()
    return redirect('index')

# --- RESTAURANT MANAGEMENT ---

def open_add_restaurant(request): 
    return render(request, 'add_restaurant.html')

def add_restaurant(request): 
    return redirect('open_show_restaurant')

def open_show_restaurant(request): 
    # This is your main dashboard after logging in
    return render(request, 'show_restaurants.html', {'restaurants': Restaurant.objects.all()})

def open_update_restaurant(request, restaurant_id): 
    res = Restaurant.objects.get(id=restaurant_id)
    return render(request, 'update_restaurant.html', {'restaurant': res})

def update_restaurant(request, restaurant_id): 
    return redirect('open_show_restaurant')

def delete_restaurant(request, restaurant_id): 
    Restaurant.objects.get(id=restaurant_id).delete()
    return redirect('open_show_restaurant')

def open_update_menu(request, restaurant_id): 
    res = Restaurant.objects.get(id=restaurant_id)
    items = Item.objects.filter(restaurant=res)
    return render(request, 'update_menu.html', {'restaurant': res, 'itemList': items})

def update_menu(request, restaurant_id): 
    return redirect('open_show_restaurant')

def view_menu(request, restaurant_id, username):
    res = Restaurant.objects.get(id=restaurant_id)
    items = Item.objects.filter(restaurant=res)
    return render(request, 'customer_menu.html', {'restaurant': res, 'items': items, 'username': username})

# --- CART & RAZORPAY ---

def add_to_cart(request, item_id, username):
    customer = Customer.objects.get(username=username)
    item = Item.objects.get(id=item_id)
    cart, _ = Cart.objects.get_or_create(customer=customer, paid=False)
    cart.items.add(item)
    return redirect('show_cart', username=username)

def show_cart(request, username):
    customer = Customer.objects.get(username=username)
    cart = Cart.objects.filter(customer=customer, paid=False).first()
    return render(request, 'cart.html', {'cart': cart, 'username': username})

def remove_from_cart(request, item_id, username):
    # 1. Fetch the customer and their active, unpaid database cart
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer, paid=False).first()
    
    if cart:
        # 2. Grab the specific item from the database
        item = get_object_or_404(Item, id=item_id)
        # 3. Safely remove it from the database relationship
        cart.items.remove(item)
        
    # 4. Redirect back to the cart view using the correct username string
    return redirect('show_cart', username=username)

def checkout(request, username):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    customer = Customer.objects.get(username=username)
    cart = Cart.objects.filter(customer=customer, paid=False).last()
    
    if not cart or not cart.items.exists():
        return render(request, 'cart.html', {'error': 'Your cart is empty', 'username': username})

    amount = int(cart.total_price() * 100)
    payment = client.order.create(data={"amount": amount, "currency": "INR", "receipt": f"rcpt_{cart.id}"})
    
    cart.razorpay_order_id = payment['id']
    cart.save()
    
    return render(request, 'checkout.html', {
        'cart': cart, 
        'payment': payment, 
        'razorpay_key_id': settings.RAZORPAY_KEY_ID, 
        'username': username
    })

@csrf_exempt
def success(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    if request.method == "POST":
        data = {
            'razorpay_order_id': request.POST.get('razorpay_order_id'),
            'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
            'razorpay_signature': request.POST.get('razorpay_signature')
        }
        try:
            client.utility.verify_payment_signature(data)
            cart = Cart.objects.get(razorpay_order_id=data['razorpay_order_id'])
            cart.paid = True
            cart.save()
            return render(request, 'success.html')
        except Exception:
            return render(request, 'fail.html')
    return redirect('index')

def orders(request, username):
    customer = Customer.objects.get(username=username)
    history = Cart.objects.filter(customer=customer, paid=True)
    return render(request, 'orders.html', {'orders': history, 'username': username})