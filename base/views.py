from .models import Cart, CartItem, Product, Profile
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from django.http import HttpRequest


User = get_user_model()

################################ Create new user and cart for the user #################################


@api_view(['POST'])
def register(request):
    data = request.data
    # Validate the data
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return Response({'error': 'Username, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
    # Check if the username or email already exists
    if User.objects.filter(username=data['username']).exists() or User.objects.filter(email=data['email']).exists():
        return Response({'error': 'Username or email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    # Create a new user
    user = User.objects.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )
  # Create a cart for the user
    cart = Cart.objects.create(user=user)
    # Associate the cart with the user
    user.user_cart = cart
    user.save()

    return Response({'message': 'Registration successful.'}, status=status.HTTP_201_CREATED)

######################## Get User ID ############################
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_id(request):
    user_id = request.user.id
    return Response({'user_id': user_id})

########################################################################
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'updated_at']

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    price = serializers.CharField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'price']


from rest_framework import status

@api_view(['GET', 'POST'])
def get_user_cart(request):
    user = request.user
    cart = user.user_cart
    print("here Get_user_cart", cart)
    if request.method == 'GET':
        # Retrieve the cart items and serialize them
        cart_items = CartItem.objects.filter(cart=cart)
        serialized_cart_items = CartItemSerializer(cart_items, many=True)

        # Return the serialized cart items in the response
        return Response({'cartItems': serialized_cart_items.data})

    elif request.method == 'POST':
        cart_items_data = request.data.get('cartItems', [])
        for item_data in cart_items_data:
            item_data['cart'] = cart.id
        serializer = CartItemSerializer(data=cart_items_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseHistorySerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['product']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_cart_history(request):
    user = request.user
    cart = user.user_cart

    # Retrieve the purchase history of the cart
    purchase_history = cart.cartitem_set.all()

    # Serialize the purchase history data
    history_serializer = PurchaseHistorySerializer(purchase_history, many=True)

    return Response(history_serializer.data)

################################ PRODUCT CRUD #################################


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image.url')

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'image_url']


class ProductViews(APIView):
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk=None):
        if pk:
            product = self.get_object(pk)
            if product:
                serializer = ProductSerializer(product)
                return Response(serializer.data)
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        prodname = request.query_params.get('prodname')
        if prodname:
            products = Product.objects.filter(name__icontains=prodname)
        else:
            products = Product.objects.all()

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        product = self.get_object(pk)
        if not product:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        product = self.get_object(pk)
        if not product:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


################################ PROFILE CRUD #################################


class ProfileSerializer(serializers.ModelSerializer):
    profileimage = serializers.ImageField(source='profileimage.url')

    class Meta:
        model = Profile
        fields = ['username', 'firstname', 'lastname', 'city', 'email', 'street', 'apartmentnumber', 'housenumber',
                  'zipcode', 'profileimage', 'is_active', 'is_staff']


class ProfileViews(APIView):
    def get_object(self, pk):
        try:
            return Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return None

    def get(self, request, pk=None):
        if pk:
            profile = self.get_object(pk)
            if profile:
                serializer = ProfileSerializer(profile)
                return Response(serializer.data)
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        firstname = request.query_params.get('firstname')
        if firstname:
            profiles = Profile.objects.filter(firstname__icontains=firstname)
        else:
            profiles = Profile.objects.all()

        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        profile = self.get_object(pk)
        if not profile:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        profile = self.get_object(pk)
        if not profile:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
